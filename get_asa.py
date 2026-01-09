import json
import sys

from algokit_utils import AlgorandClient, AssetInformation

from setup import get_algorand_client, get_caller_signer

DEFAULT_GET_ASSET_ID = 753358221


def get_asset(algorand_client: AlgorandClient, asset_id: int) -> AssetInformation:
    """Get an asset."""
    return algorand_client.asset.get_by_id(asset_id)


def main() -> int:
    """Get an asset on the configured network."""
    algorand_client = get_algorand_client()
    caller = get_caller_signer()
    algorand_client.account.set_signer(caller.address, caller.signer)

    asset_id = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_GET_ASSET_ID
    asset_result = get_asset(algorand_client, asset_id)

    print(json.dumps(asset_result.__dict__, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
