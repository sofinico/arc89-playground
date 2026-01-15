"""
Read ARC-89 metadata from the registry.

Prerequisites:
- Run `make setup`
"""

import json
import logging

from algokit_utils import AlgorandClient
from asa_metadata_registry import AsaMetadataRegistry, AssetMetadataRecord, MetadataSource

from config import config
from utils import check_existence, get_algorand_client, get_asset_id

logger = logging.getLogger(__name__)

# ==========================================================================================================
# GET METADATA PARAMS - Edit these values for your use case
# ==========================================================================================================

# Set this to override the `ASSET_ID` env variable (or leave as None to use env var)
ASSET_ID: int | None = None
# ==========================================================================================================


def get_metadata(algorand_client: AlgorandClient, asset_id: int) -> AssetMetadataRecord:
    registry_readonly = AsaMetadataRegistry.from_algod(
        algod=algorand_client.client.algod,
        app_id=config.metadata_registry_app_id,
    )
    check_existence(registry_readonly, asset_id)

    return registry_readonly.read.get_asset_metadata(
        asset_id=asset_id,
        source=MetadataSource.BOX,
    )


def main() -> int:
    """Get metadata for an ASA on the configured network."""
    algorand_client = get_algorand_client()
    asset_id = get_asset_id(ASSET_ID)

    record = get_metadata(algorand_client, asset_id)
    metadata_json = record.json

    logger.info(
        f"\nAsset Metadata Record for {asset_id}:\n"
        f"  Registry App ID: {record.app_id}\n"
        f"  Asset ID: {record.asset_id}\n"
        f"  Metadata size: {record.body.size} bytes\n"
        f"  Is short: {record.body.is_short}\n"
        f"  Is empty: {record.body.is_empty}"
    )

    logger.info(
        f"\nMetadata Header:\n"
        f"  Identifiers byte: {record.header.identifiers:#04x}\n"
        f"  Is short (from identifiers): {record.header.is_short}\n"
        f"  Is immutable: {record.header.is_immutable}\n"
        f"  Is ARC-3 compliant: {record.header.is_arc3_compliant}\n"
        f"  Is ARC-89 native: {record.header.is_arc89_native}\n"
        f"  Is deprecated: {record.header.is_deprecated}\n"
        f"  Last modified round: {record.header.last_modified_round}\n"
        f"  Metadata hash: {record.header.metadata_hash.hex()}"
    )

    logger.info(f"\nMetadata JSON:\n" f"{json.dumps(metadata_json, indent=2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
