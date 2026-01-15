import os

from algokit_utils import AlgorandClient, AssetInformation


def get_asset_id(asset_id: int | None = None) -> int:
    if asset_id is not None:
        return asset_id

    asset_id_str = os.getenv("ASSET_ID")
    if not asset_id_str:
        raise ValueError("ASSET_ID must be set as parameter or environment variable")
    return int(asset_id_str)


def get_asset(algorand_client: AlgorandClient, asset_id: int) -> AssetInformation:
    return algorand_client.asset.get_by_id(asset_id)
