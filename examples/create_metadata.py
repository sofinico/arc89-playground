"""
Create ARC-89 metadata for an existing ASA.

Prerequisites:
- Run `make setup`
- In testnet, CALLER_MNEMONIC's account must be funded to operate. See https://lora.algokit.io/testnet/fund.
- The CALLER is the manager of the ASA (already satisfied if ASA was created via `make create-asa`).
"""

import logging

from algokit_utils import (
    AlgorandClient,
    SigningAccount,
)
from asa_metadata_registry import (
    AsaMetadataRegistry,
    AssetMetadata,
    IrreversibleFlags,
    MbrDelta,
    MetadataFlags,
    MetadataSource,
    ReversibleFlags,
    complete_partial_asset_url,
)
from asa_metadata_registry._generated.asa_metadata_registry_client import AsaMetadataRegistryClient

from config import config
from utils.runtime import get_algorand_client, get_caller_signer
from utils.utils import get_asset, get_asset_id

logger = logging.getLogger(__name__)

# ==========================================================================================================
# METADATA CREATION PARAMS - Edit these values for your use case
# ==========================================================================================================

# Set this to override the `ASSET_ID` env variable (or leave as None to use env var)
ASSET_ID: int | None = None

METADATA_FLAGS = MetadataFlags(
    reversible=ReversibleFlags(
        arc20=False,  # ARC-20 compliance (reversible)
        arc62=False,  # ARC-62 compliance (reversible)
    ),
    irreversible=IrreversibleFlags(
        arc3=False,  # ARC-3 compliance (requires ARC-3 URL/name formatting)
        arc89_native=True,  # Enforces ARC-90 URI prefix in the ASA URL
        immutable=False,  # Prevents future metadata updates if True
    ),
)

METADATA_JSON = {
    "name": "ARC-89 & ARC-90 Compliance ASA Example",
    "description": "Example metadata written to the ARC-89 registry.",
    "version": 1,
}

DEPRECATED_BY = 0
# ==========================================================================================================


def _check_existence(registry: AsaMetadataRegistry, asset_id: int) -> None:
    existence = registry.read.arc89_check_metadata_exists(
        asset_id=asset_id,
        source=MetadataSource.BOX,
    )
    if not existence.asa_exists:
        raise Exception(f"ASA {asset_id} does not exist")
    if existence.metadata_exists:
        raise Exception(f"Metadata already exists for asset {asset_id}")


def create_metadata(
    algorand_client: AlgorandClient, caller: SigningAccount, asset_id: int
) -> tuple[AssetMetadata, MbrDelta]:
    app_client = algorand_client.client.get_typed_app_client_by_id(
        AsaMetadataRegistryClient,
        app_id=config.metadata_registry_app_id,
        default_sender=caller.address,
        default_signer=caller.signer,
    )
    registry = AsaMetadataRegistry.from_app_client(app_client, algod=algorand_client.client.algod)
    _check_existence(registry, asset_id)

    metadata = AssetMetadata.from_json(
        asset_id=asset_id,
        json_obj=METADATA_JSON,
        flags=METADATA_FLAGS,
        deprecated_by=DEPRECATED_BY,
        arc3_compliant=METADATA_FLAGS.irreversible.arc3,
    )

    mbrDelta = registry.write.create_metadata(asset_manager=caller, metadata=metadata)
    return metadata, mbrDelta


def main() -> int:
    """Create metadata for an ASA on the configured network."""
    caller = get_caller_signer()
    algorand_client = get_algorand_client()
    asset_id = get_asset_id(ASSET_ID)
    asset = get_asset(algorand_client, asset_id)

    metadata, mbrDelta = create_metadata(algorand_client, caller, asset_id)

    logger.info(f"Created metadata - Asset ID: {metadata.asset_id}")
    logger.info(f"ARC-90 URI: {complete_partial_asset_url(asset.url or '', asset_id)}")
    logger.info(f"Minimum Balance Requirement (MBR) delta: {mbrDelta.amount}")
    logger.info(f"ARC-89 metadata hash: {metadata.compute_arc89_metadata_hash().hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
