"""
Delete ARC-89 metadata for an existing ASA.

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
    MbrDelta,
)
from asa_metadata_registry._generated.asa_metadata_registry_client import AsaMetadataRegistryClient

from config import config
from utils import check_existence, get_algorand_client, get_asset_id, get_caller_signer

logger = logging.getLogger(__name__)

# ==========================================================================================================
# DELETE METADATA PARAMS - Edit these values for your use case
# ==========================================================================================================

# Set this to override the `ASSET_ID` env variable (or leave as None to use env var)
ASSET_ID: int | None = None
# ==========================================================================================================


def delete_metadata(algorand_client: AlgorandClient, caller: SigningAccount, asset_id: int) -> MbrDelta:
    app_client = algorand_client.client.get_typed_app_client_by_id(
        AsaMetadataRegistryClient,
        app_id=config.metadata_registry_app_id,
        default_sender=caller.address,
        default_signer=caller.signer,
    )
    registry = AsaMetadataRegistry.from_app_client(app_client, algod=algorand_client.client.algod)
    check_existence(registry, asset_id, True)

    mbr_result = registry.write.delete_metadata(
        asset_manager=caller,
        asset_id=asset_id,
    )
    return mbr_result


def main() -> int:
    """Delete metadata for an ASA on the configured network."""
    caller = get_caller_signer()
    algorand_client = get_algorand_client()
    asset_id = get_asset_id(ASSET_ID)

    mbr_result = delete_metadata(algorand_client, caller, asset_id)

    logger.info(f"Deleted metadata - Asset ID: {asset_id}")
    logger.info(f"Minimum Balance Requirement (MBR) delta: -{mbr_result.amount}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
