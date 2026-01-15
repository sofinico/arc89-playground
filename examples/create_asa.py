"""
Create an ARC-90 compliant ASA.

Prerequisites:
- Run `make setup`
- In testnet, CALLER_MNEMONIC's account must be funded to operate. See https://lora.algokit.io/testnet/fund.
"""

import json
import logging
from typing import Any

from algokit_utils import AlgorandClient
from algokit_utils.transactions import AssetCreateParams
from asa_metadata_registry import Arc90Compliance, Arc90Uri
from dotenv import set_key

from config import config
from utils.runtime import get_algorand_client, get_caller_address

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


def _create_partial_arc90_uri(compliance: Arc90Compliance | None = None) -> str:
    if compliance is None:
        compliance = ARC90_COMPLIANCE
    partial_uri = Arc90Uri(
        netauth=config.arc90_netauth,
        app_id=config.metadata_registry_app_id,
        box_name=None,  # partial: no box value
        compliance=compliance,
    )
    uri = partial_uri.to_uri()
    logger.info(f"Created partial ARC-90 URI: {uri}")
    return uri


def create_asset(algorand_client: AlgorandClient, sender_address: str) -> Any:
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
            url=_create_partial_arc90_uri(ARC90_COMPLIANCE),
            metadata_hash=METADATA_HASH,
        )
    )
    logger.info(f"Created asset: {result}")
    return result


def main() -> int:
    """Create an ASA on the configured network."""
    algorand_client = get_algorand_client()
    caller_address = get_caller_address()

    fungible_result = create_asset(algorand_client, caller_address)

    result_info = {
        "asset_id": fungible_result.asset_id,
        "tx_id": fungible_result.tx_id,
        "confirmed_round": fungible_result.confirmation.get("confirmed-round"),
    }
    logger.info(json.dumps(result_info, indent=2))

    set_key(config.env_path, "ASSET_ID", str(fungible_result.asset_id), quote_mode="never", export=True)
    logger.info(f"Updated {config.env_path.name} with ASSET_ID={fungible_result.asset_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
