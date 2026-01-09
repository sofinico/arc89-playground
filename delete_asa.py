import json
import os
import sys

from algokit_utils import AlgorandClient
from algokit_utils.transactions import AssetDestroyParams

from setup import get_algorand_client, get_caller_signer

DEFAULT_DELETE_ASSET_ID = int(os.getenv("ASSET_ID", "0"))


def delete_asset(algorand_client: AlgorandClient, sender_address: str, asset_id: int) -> None:
    algorand_client.send.asset_destroy(
        AssetDestroyParams(
            sender=sender_address,
            asset_id=asset_id,
        )
    )


def main() -> int:
    algorand_client = get_algorand_client()
    caller = get_caller_signer()

    asset_id = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DELETE_ASSET_ID
    if not asset_id:
        raise ValueError("Provide asset id or set ASSET_ID")

    delete_asset(algorand_client, caller.address, asset_id)

    print(json.dumps({"asset_id": asset_id, "deleted": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
