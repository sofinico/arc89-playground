"""
Delete an ASA by ID.
"""

import logging

from config import config  # noqa: F401 - Loads environment variables
from utils import delete_asset, get_algorand_client, get_asset_id, get_caller_address

logger = logging.getLogger(__name__)

# ==========================================================================================================
# DELETE ASA PARAMS - Edit these values for your use case
# ==========================================================================================================

# Set this to override the `ASSET_ID` env variable (or leave as None to use env var)
ASSET_ID: int | None = None
# ==========================================================================================================


def main() -> int:
    """Delete an ASA on the configured network."""
    algorand_client = get_algorand_client()
    caller_address = get_caller_address()
    asset_id = get_asset_id(ASSET_ID)

    result = delete_asset(algorand_client, caller_address, asset_id)

    logger.info(f"Asset {asset_id} deleted successfully")
    logger.info(f"Tx ID: {result.tx_id}")
    if isinstance(result.confirmation, dict):
        logger.info(f"Confirmed round: {result.confirmation.get('confirmed-round')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
