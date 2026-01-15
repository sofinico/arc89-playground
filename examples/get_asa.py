"""
Fetch ASA details from the configured network.
"""

import json
import logging

from config import config  # noqa: F401 - Loads environment variables
from utils import get_algorand_client, get_asset, get_asset_id

logger = logging.getLogger(__name__)

# ==========================================================================================================
# GET ASA PARAMS - Edit these values for your use case
# ==========================================================================================================

# Set this to override the `ASSET_ID` env variable (or leave as None to use env var)
ASSET_ID: int | None = None
# ==========================================================================================================


def main() -> int:
    """Get an asset on the configured network."""
    algorand_client = get_algorand_client()
    asset_id = get_asset_id(ASSET_ID)

    result = get_asset(algorand_client, asset_id)

    logger.info(json.dumps(result.__dict__, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
