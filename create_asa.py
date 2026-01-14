from __future__ import annotations

import json
import logging
from typing import Any

from algokit_utils import AlgorandClient
from algokit_utils.transactions import AssetCreateParams
from asa_metadata_registry import Arc90Compliance, Arc90Uri

from setup import config, get_algorand_client, get_caller_address

logger = logging.getLogger(__name__)


def _create_partial_arc90_uri(compliance: Arc90Compliance | None = None) -> str:
    if compliance is None:
        compliance = Arc90Compliance(arcs=(89, 90))
    partial_uri = Arc90Uri(
        netauth=config.arc90_netauth,
        app_id=config.metadata_registry_app_id,
        box_name=None,  # partial - no box value
        compliance=compliance,
    )
    uri = partial_uri.to_uri()
    logger.info(f"Created partial ARC-90 URI: {uri}")
    return uri


def create_asset(algorand_client: AlgorandClient, sender_address: str) -> Any:
    """Create a fungible ASA."""
    # NOTE: Configure ASA parameters below
    result = algorand_client.send.asset_create(
        AssetCreateParams(
            sender=sender_address,
            total=89_000_000_000_000,
            decimals=0,
            default_frozen=False,
            manager=sender_address,
            reserve=sender_address,
            freeze=sender_address,
            clawback=sender_address,
            unit_name="ENT",
            asset_name="Eightynine Ninety Token",
            url=_create_partial_arc90_uri(Arc90Compliance(arcs=(89, 90))),
            metadata_hash=b"\x00" * 32,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
