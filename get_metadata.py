import json
import os
import sys

from algokit_utils import AlgorandClient
from asa_metadata_registry.algod import AlgodBoxReader

from setup import config, get_algorand_client, get_caller_signer

DEFAULT_GET_METADATA_ASSET_ID = int(os.getenv("ASSET_ID", "0"))


def get_metadata(
    algorand_client: AlgorandClient, app_id: int, asset_id: int
) -> dict[str, object]:
    reader = AlgodBoxReader(algod=algorand_client.client.algod)
    record = reader.get_asset_metadata_record(app_id=app_id, asset_id=asset_id)
    header = record.header
    header_dict = {
        "identifiers_byte": header.identifiers,
        "reversible_flags_byte": header.flags.reversible_byte,
        "irreversible_flags_byte": header.flags.irreversible_byte,
        "metadata_hash_hex": header.metadata_hash.hex(),
        "last_modified_round": header.last_modified_round,
        "deprecated_by": header.deprecated_by,
    }
    return {"header": header_dict, "metadata": record.json}


def main() -> int:
    algorand_client = get_algorand_client()
    caller = get_caller_signer()
    algorand_client.account.set_signer(caller.address, caller.signer)

    asset_id = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_GET_METADATA_ASSET_ID
    if not asset_id:
        raise ValueError("Provide asset id or set ASSET_ID")

    app_id = config.metadata_registry_app_id
    if not app_id:
        raise ValueError("METADATA_REGISTRY_APP_ID is not configured")

    metadata = get_metadata(algorand_client, app_id, asset_id)
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
