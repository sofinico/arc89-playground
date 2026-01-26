"""
Create ARC-89 metadata for an existing ASA.

Prerequisites:
- Run `make setup`
- In testnet, CALLER_MNEMONIC's account must be funded to operate. See https://lora.algokit.io/testnet/fund.
- The CALLER is the manager of the ASA (already satisfied if ASA was created via `make create-asa`).
"""

import argparse
import json
import logging
import os
from pathlib import Path

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
    ReversibleFlags,
    complete_partial_asset_url,
    is_arc3_metadata,
)
from asa_metadata_registry._generated.asa_metadata_registry_client import AsaMetadataRegistryClient

from config import config
from utils import check_existence, get_asset
from utils.prompts import prompt_int, prompt_metadata_flags
from utils.runtime import get_algorand_client, get_caller_signer

logger = logging.getLogger(__name__)

# ==========================================================================================================
# METADATA CREATION DEFAULTS
# ==========================================================================================================

DEFAULT_METADATA_JSON_PATH = Path("metadata/example.json")

DEFAULT_REVERSIBLE_FLAGS = ReversibleFlags(
    arc20=False,  # ARC-20 compliance (reversible)
    arc62=False,  # ARC-62 compliance (reversible)
)

DEPRECATED_BY = 0

DEFAULT_IRREVERSIBLE_FLAGS = IrreversibleFlags(
    arc3=False,  # ARC-3 compliance (requires ARC-3 URL/name formatting)
    arc89_native=True,  # Enforces ARC-90 URI prefix in the ASA URL
    immutable=False,  # Prevents future metadata updates if True
)
# ==========================================================================================================


def default_metadata_flags() -> MetadataFlags:
    return MetadataFlags(
        reversible=ReversibleFlags(
            arc20=DEFAULT_REVERSIBLE_FLAGS.arc20,
            arc62=DEFAULT_REVERSIBLE_FLAGS.arc62,
        ),
        irreversible=IrreversibleFlags(
            arc3=DEFAULT_IRREVERSIBLE_FLAGS.arc3,
            arc89_native=DEFAULT_IRREVERSIBLE_FLAGS.arc89_native,
            immutable=DEFAULT_IRREVERSIBLE_FLAGS.immutable,
        ),
    )


def create_metadata(
    algorand_client: AlgorandClient,
    caller: SigningAccount,
    asset_id: int,
    metadata_json: dict[str, object],
    metadata_flags: MetadataFlags,
) -> tuple[AssetMetadata, MbrDelta]:
    app_client = algorand_client.client.get_typed_app_client_by_id(
        AsaMetadataRegistryClient,
        app_id=config.metadata_registry_app_id,
        default_sender=caller.address,
        default_signer=caller.signer,
    )
    registry = AsaMetadataRegistry.from_app_client(app_client, algod=algorand_client.client.algod)
    check_existence(registry, asset_id, False)

    metadata = AssetMetadata.from_json(
        asset_id=asset_id,
        json_obj=metadata_json,
        flags=metadata_flags,
        deprecated_by=DEPRECATED_BY,
        arc3_compliant=is_arc3_metadata(metadata_json),
    )

    mbr_result = registry.write.create_metadata(asset_manager=caller, metadata=metadata)
    return metadata, mbr_result


def load_metadata_json(path_str: str | Path) -> dict[str, object]:
    path = Path(path_str)
    if not path.is_file():
        raise FileNotFoundError(f"Metadata JSON file not found: {path}")
    with path.open(encoding="utf-8") as f:
        metadata_json = json.load(f)
    if not isinstance(metadata_json, dict):
        raise ValueError("Metadata JSON must be a JSON object at the top level")
    return metadata_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create ARC-89 metadata for an ASA.")
    parser.add_argument(
        "--metadata-json",
        help=(
            "Path to a JSON file to use as metadata "
            f"(or set METADATA_JSON_PATH, default: {DEFAULT_METADATA_JSON_PATH})."
        ),
    )
    parser.add_argument(
        "--asset-id",
        type=int,
        help="ASA ID (defaults to ASSET_ID if set).",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Run non-interactively; use defaults and env/flags only.",
    )
    return parser.parse_args()


def resolve_metadata_json_path(args: argparse.Namespace) -> str | Path:
    if args.metadata_json:
        return str(args.metadata_json)
    env_path = os.getenv("METADATA_JSON_PATH")
    if env_path:
        return env_path
    return DEFAULT_METADATA_JSON_PATH


def resolve_asset_id(args: argparse.Namespace) -> int:
    asset_id_default: int | None = args.asset_id
    if asset_id_default is None:
        env_asset_id = os.getenv("ASSET_ID")
        asset_id_default = int(env_asset_id) if env_asset_id else None
    if args.no_prompt:
        if asset_id_default is None:
            raise ValueError("Provide --asset-id or set ASSET_ID when using --no-prompt.")
        return asset_id_default
    return prompt_int("Asset ID", asset_id_default)


def resolve_metadata_flags(args: argparse.Namespace) -> MetadataFlags:
    if args.no_prompt:
        return default_metadata_flags()
    return prompt_metadata_flags(DEFAULT_REVERSIBLE_FLAGS, DEFAULT_IRREVERSIBLE_FLAGS)


def main() -> int:
    """Create metadata for an ASA on the configured network."""
    args = parse_args()
    metadata_json_path = resolve_metadata_json_path(args)

    caller = get_caller_signer()
    algorand_client = get_algorand_client()
    asset_id = resolve_asset_id(args)
    asset = get_asset(algorand_client, asset_id)
    metadata_json = load_metadata_json(metadata_json_path)
    metadata_flags = resolve_metadata_flags(args)

    metadata, mbrDelta = create_metadata(
        algorand_client,
        caller,
        asset_id,
        metadata_json,
        metadata_flags,
    )

    logger.info(f"Created metadata - Asset ID: {metadata.asset_id}")
    logger.info(f"ARC-90 URI: {complete_partial_asset_url(asset.url or '', asset_id)}")
    logger.info(f"Minimum Balance Requirement (MBR) delta: {mbrDelta.amount}")
    logger.info(f"ARC-89 metadata hash: {metadata.compute_arc89_metadata_hash().hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
