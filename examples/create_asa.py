"""
Create an ARC-90 compliant ASA.

Prerequisites:
- Run `make setup`
- In testnet, CALLER_MNEMONIC's account must be funded to operate. See https://lora.algokit.io/testnet/fund.
"""

import logging

from algokit_utils import AlgorandClient, SendSingleAssetCreateTransactionResult
from algokit_utils.transactions import AssetCreateParams
from asa_metadata_registry import Arc90Compliance, Arc90Uri
from dotenv import set_key

from config import config
from utils import get_algorand_client, get_caller_address

logger = logging.getLogger(__name__)

# ==========================================================================================================
# ASA CREATION PARAMS - Edit these values for your use case
# ==========================================================================================================

TOTAL_SUPPLY = 89_000_000_000_000
DECIMALS = 6
UNIT_NAME = "ENT"
ASSET_NAME = "Eightynine Ninety Token"
ARC90_COMPLIANCE = Arc90Compliance(arcs=(89, 90))  # ARC-90 URI's declared compliance

# For an ARC-89 compliant and NOT immutable ASA, the Asset Metadata Hash `am` must be set to a zero bytes at
# creation. See https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0089.md#asset-metadata-hash.
METADATA_HASH = b"\x00" * 32

# By default, manager, reserve, freeze, and clawback are set to the CALLER_MNEMONIC's address.
# To override these, modify the parameters in the `create_asset` function below.
# ==========================================================================================================


def get_arc90_partial_uri(compliance: Arc90Compliance = ARC90_COMPLIANCE) -> str:
    return Arc90Uri(
        netauth=config.arc90_netauth, app_id=config.metadata_registry_app_id, box_name=None, compliance=compliance
    ).to_uri()


def create_asset(algorand_client: AlgorandClient, sender_address: str) -> SendSingleAssetCreateTransactionResult:
    result = algorand_client.send.asset_create(
        AssetCreateParams(
            sender=sender_address,
            total=TOTAL_SUPPLY,
            decimals=DECIMALS,
            default_frozen=False,
            manager=sender_address,
            reserve=sender_address,
            freeze=sender_address,
            clawback=sender_address,
            unit_name=UNIT_NAME,
            asset_name=ASSET_NAME,
            url=get_arc90_partial_uri(ARC90_COMPLIANCE),
            metadata_hash=METADATA_HASH,
        )
    )
    return result


def main() -> int:
    """Create an ASA on the configured network."""
    algorand_client = get_algorand_client()
    caller_address = get_caller_address()

    result = create_asset(algorand_client, caller_address)

    logger.info(f"Asset ID: {result.asset_id}")
    logger.info(f"ARC-90 partial URI: {get_arc90_partial_uri(ARC90_COMPLIANCE)}")
    logger.info(f"Tx ID: {result.tx_id}")
    if isinstance(result.confirmation, dict):
        logger.info(f"Confirmed round: {result.confirmation.get('confirmed-round')}")

    asset_id_var = f"ASSET_ID_{config.network.upper()}"
    set_key(config.env_path, asset_id_var, str(result.asset_id), quote_mode="never")
    logger.info(f"Updated {config.env_path.name} with {asset_id_var}={result.asset_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
