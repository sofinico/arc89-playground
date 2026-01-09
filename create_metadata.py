"""
Create ARC-89 metadata for an existing ASA.

The registry stores a header + body. You only provide the body (JSON bytes) and flags;
the header is derived and stored on-chain:
- identifiers byte (shortness bit derived from size)
- reversible flags byte (ARC-20 / ARC-62)
- irreversible flags byte (ARC-3 / ARC-89 native / immutable)
- hash fields computed from identifiers, flags, and metadata pages
- last modified + deprecated_by tracked by the registry
"""

import json
from typing import Any

from algokit_utils import (
    AlgoAmount,
    AlgorandClient,
    CommonAppCallParams,
    PaymentParams,
    SendParams,
    SigningAccount,
)
from asa_metadata_registry import (
    Arc90Uri,
    AssetMetadata,
    IrreversibleFlags,
    MetadataFlags,
    ReversibleFlags,
    constants as arc_consts,
)
from asa_metadata_registry._generated.asa_metadata_registry_client import (
    Arc89CheckMetadataExistsArgs,
    Arc89CreateMetadataArgs,
    Arc89ExtraPayloadArgs,
    AsaMetadataRegistryClient,
)

from setup import config, get_algorand_client, get_caller_signer


def _resolve_registry(
    algorand_client: AlgorandClient,
    caller: SigningAccount,
) -> tuple[AsaMetadataRegistryClient, str]:
    app_id = config.metadata_registry_app_id
    netauth = config.arc90_netauth

    if not app_id:
        raise ValueError("METADATA_REGISTRY_APP_ID is not configured")
    if not netauth:
        raise ValueError("ARC90_NETAUTH is not configured")

    app_client = algorand_client.client.get_typed_app_client_by_id(
        AsaMetadataRegistryClient,
        app_id=app_id,
        default_sender=caller.address,
        default_signer=caller.signer,
    )
    return app_client, netauth


def _get_min_fee(client: AsaMetadataRegistryClient) -> int:
    return int(client.algorand.get_suggested_params().min_fee)


def _create_mbr_payment_txn(
    client: AsaMetadataRegistryClient,
    sender: SigningAccount,
    amount: int,
) -> Any:
    return client.algorand.create_transaction.payment(
        PaymentParams(
            sender=sender.address,
            receiver=client.app_address,
            amount=AlgoAmount(micro_algo=amount),
            static_fee=AlgoAmount(micro_algo=0),
        ),
    )


def _get_asset_params(algorand_client: AlgorandClient, asset_id: int) -> dict[str, Any]:
    try:
        info = algorand_client.client.algod.asset_info(asset_id)
    except Exception as exc:
        raise ValueError(f"Asset {asset_id} not found on network") from exc
    params = info.get("params", {})
    if not isinstance(params, dict):
        raise ValueError(f"Unexpected asset params for {asset_id}")
    return params


def _is_arc3_compliant(asset_params: dict[str, Any]) -> bool:
    name = str(asset_params.get("name") or "")
    url = str(asset_params.get("url") or "")
    if name == arc_consts.ARC3_NAME.decode():
        return True
    if name.endswith(arc_consts.ARC3_NAME_SUFFIX.decode()):
        return True
    if url.endswith(arc_consts.ARC3_URL_SUFFIX.decode()):
        return True
    return False


def _assert_preconditions(
    algorand_client: AlgorandClient,
    caller: SigningAccount,
    client: AsaMetadataRegistryClient,
    *,
    netauth: str,
    asset_id: int,
    flags: MetadataFlags,
) -> None:
    params = _get_asset_params(algorand_client, asset_id)
    manager = str(params.get("manager") or "")
    if not manager:
        raise ValueError("ASA has no manager; metadata updates are not permitted")
    if manager != caller.address:
        raise ValueError(
            f"Caller must be ASA manager (manager={manager}, caller={caller.address})"
        )
    if flags.irreversible.arc3 and not _is_arc3_compliant(params):
        raise ValueError("ARC-3 flag set but ASA is not ARC-3 compliant")
    if flags.irreversible.arc89_native:
        partial_uri = Arc90Uri(
            netauth=netauth,
            app_id=client.app_id,
            box_name=None,
        ).to_uri()
        url = str(params.get("url") or "")
        if not url.startswith(partial_uri):
            raise ValueError(
                "ARC-89 native flag set but ASA URL does not start with the "
                "ARC-90 partial URI"
            )

    existence = client.send.arc89_check_metadata_exists(
        args=Arc89CheckMetadataExistsArgs(asset_id=asset_id)
    ).abi_return
    if existence and existence.metadata_exists:
        raise ValueError("Metadata already exists for this ASA")


def _describe_headers(metadata: AssetMetadata) -> dict[str, Any]:
    return {
        "metadata_size_bytes": metadata.body.size,
        "identifiers_byte": metadata.identifiers_byte,
        "reversible_flags_byte": metadata.flags.reversible_byte,
        "irreversible_flags_byte": metadata.flags.irreversible_byte,
        "is_short": metadata.is_short,
        "header_hash_hex": metadata.compute_header_hash().hex(),
        "arc89_metadata_hash_hex": metadata.compute_arc89_metadata_hash().hex(),
        "deprecated_by": metadata.deprecated_by,
    }


def create_arc89_metadata(
    algorand_client: AlgorandClient,
    caller: SigningAccount,
    *,
    asset_id: int,
    metadata_obj: dict[str, object],
    flags: MetadataFlags,
    deprecated_by: int,
) -> str:
    client, netauth = _resolve_registry(
        algorand_client,
        caller,
    )

    _assert_preconditions(
        algorand_client,
        caller,
        client,
        netauth=netauth,
        asset_id=asset_id,
        flags=flags,
    )

    metadata = AssetMetadata.from_json(
        asset_id=asset_id,
        json_obj=metadata_obj,
        flags=flags,
        deprecated_by=deprecated_by,
        arc3_compliant=flags.irreversible.arc3,
    )

    # Header definition (stored by the registry, not supplied by the client):
    # - identifiers byte: shortness bit (derived from metadata size)
    # - reversible flags byte: ARC-20 / ARC-62 (mutable)
    # - irreversible flags byte: ARC-3 / ARC-89 native / immutable (write-once)
    # - metadata hash: computed from identifiers, flags, and metadata pages
    # - last_modified_round + deprecated_by: maintained by the registry
    header_info = _describe_headers(metadata)

    mbr_delta = metadata.get_mbr_delta(old_size=None)
    mbr_payment = _create_mbr_payment_txn(
        client, caller, int(mbr_delta.amount)
    )

    chunks = metadata.body.chunked_payload()
    total_fee = (len(chunks) + 2) * _get_min_fee(client)

    composer = client.new_group()
    composer.arc89_create_metadata(
        args=Arc89CreateMetadataArgs(
            asset_id=asset_id,
            reversible_flags=metadata.flags.reversible_byte,
            irreversible_flags=metadata.flags.irreversible_byte,
            metadata_size=metadata.body.size,
            payload=chunks[0],
            mbr_delta_payment=mbr_payment,
        ),
        params=CommonAppCallParams(
            sender=caller.address,
            static_fee=AlgoAmount(micro_algo=total_fee),
        ),
    )

    for chunk in chunks[1:]:
        composer.arc89_extra_payload(
            args=Arc89ExtraPayloadArgs(
                asset_id=asset_id,
                payload=chunk,
            ),
            params=CommonAppCallParams(
                sender=caller.address,
                static_fee=AlgoAmount(micro_algo=0),
            ),
        )

    response = composer.send(
        send_params=SendParams(cover_app_call_inner_transaction_fees=True)
    )

    asset_info = algorand_client.client.algod.asset_info(asset_id)
    asset_params = asset_info.get("params", {})
    asset_url = str(asset_params.get("url") or "")
    if not asset_url:
        raise ValueError("ASA URL is missing; cannot build ARC-90 URI")
    partial_uri = Arc90Uri.parse(asset_url)
    metadata_uri = partial_uri.with_asset_id(asset_id).to_uri()

    result = {
        "app_id": client.app_id,
        "asset_id": asset_id,
        "arc90_metadata_uri": metadata_uri,
        "metadata_json": metadata_obj,
        "flags": {
            "arc3": metadata.flags.irreversible.arc3,
            "arc89_native": metadata.flags.irreversible.arc89_native,
            "immutable": metadata.flags.irreversible.immutable,
            "arc20": metadata.flags.reversible.arc20,
            "arc62": metadata.flags.reversible.arc62,
        },
        "header": header_info,
        "tx_ids": response.tx_ids,
    }
    return json.dumps(result, indent=2)


def main() -> int:
    algorand_client = get_algorand_client()
    caller = get_caller_signer()

    # NOTE: Configure your asset id, metadata, flags, and deprecated_by here.
    output = create_arc89_metadata(
        algorand_client,
        caller,
        asset_id=753492624,
        metadata_obj={
            "name": "ARC-89 & ARC-90 Compliance ASA Example",
            "description": "Example metadata written to the ARC-89 registry.",
            "version": 1,
        },
        flags=MetadataFlags(
            reversible=ReversibleFlags(arc20=False, arc62=False),
            irreversible=IrreversibleFlags(arc3=False, arc89_native=True, immutable=False),
        ),
        deprecated_by=0,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
