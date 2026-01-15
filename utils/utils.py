import os

from algokit_utils import AlgorandClient, AssetDestroyParams, AssetInformation, SendSingleTransactionResult
from asa_metadata_registry import AsaMetadataRegistry, MetadataSource


def get_asset_id(asset_id: int | None = None) -> int:
    if asset_id is not None:
        return asset_id

    asset_id_str = os.getenv("ASSET_ID")
    if not asset_id_str:
        raise ValueError("ASSET_ID must be set as parameter or environment variable")
    return int(asset_id_str)


def get_asset(algorand_client: AlgorandClient, asset_id: int) -> AssetInformation:
    return algorand_client.asset.get_by_id(asset_id)


def delete_asset(algorand_client: AlgorandClient, sender_address: str, asset_id: int) -> SendSingleTransactionResult:
    return algorand_client.send.asset_destroy(
        AssetDestroyParams(
            sender=sender_address,
            asset_id=asset_id,
        )
    )


def check_existence(registry: AsaMetadataRegistry, asset_id: int, needs_metadata: bool = True) -> None:
    """Check asset and metadata existence."""
    existence = registry.read.arc89_check_metadata_exists(
        asset_id=asset_id,
        source=MetadataSource.BOX,
    )
    if not existence.asa_exists:
        raise Exception(f"ASA {asset_id} does not exist")
    if existence.metadata_exists and not needs_metadata:
        raise Exception(f"Metadata already exists for asset {asset_id}")
    if not existence.metadata_exists and needs_metadata:
        raise Exception(f"Metadata does not exist for asset {asset_id}")
