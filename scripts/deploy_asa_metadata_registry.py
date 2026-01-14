import argparse
import logging
import os
from pathlib import Path

from algokit_utils import AlgoAmount, AlgorandClient, AppClientCompilationParams, PaymentParams, SigningAccount
from asa_metadata_registry import Arc90Uri
from asa_metadata_registry import constants as const
from asa_metadata_registry._generated.asa_metadata_registry_client import (
    AsaMetadataRegistryFactory,
)
from dotenv import load_dotenv, set_key

logger = logging.getLogger(__name__)
project_root = Path(__file__).resolve().parent.parent


def _get_deployer(algorand: AlgorandClient) -> SigningAccount:
    deployer = algorand.account.random()
    dispenser = algorand.account.localnet_dispenser()
    algorand.account.ensure_funded(deployer.address, dispenser, AlgoAmount.from_algo(10))
    return deployer


def deploy(write_env: bool) -> int:
    algorand = AlgorandClient.from_environment()
    deployer = _get_deployer(algorand)
    algorand.account.set_signer(deployer.address, deployer.signer)

    factory = algorand.client.get_typed_app_factory(
        AsaMetadataRegistryFactory,
        compilation_params=AppClientCompilationParams(
            deploy_time_params={
                "TRUSTED_DEPLOYER": deployer.public_key,
                "ARC90_NETAUTH": os.environ["ARC90_NETAUTH"],
            }
        ),
        default_sender=deployer.address,
        default_signer=deployer.signer,
    )

    app_client, _ = factory.send.create.bare()
    algorand.send.payment(
        PaymentParams(
            sender=deployer.address,
            receiver=app_client.app_address,
            amount=AlgoAmount(micro_algo=const.ACCOUNT_MBR),
        )
    )

    partial_uri = Arc90Uri(netauth=os.environ["ARC90_NETAUTH"], app_id=app_client.app_id, box_name=None).to_uri()

    logger.info("ASA Metadata Registry deployed")
    logger.info("App ID: %s", app_client.app_id)
    logger.info("ARC-90 Partial URI: %s", partial_uri)

    if write_env:
        env_path = project_root / ".env.localnet"
        set_key(env_path, "METADATA_REGISTRY_APP_ID", str(app_client.app_id))
        logger.info("Updated %s with METADATA_REGISTRY_APP_ID", env_path)

    return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    load_dotenv(dotenv_path=project_root / ".env")
    network = os.getenv("NETWORK", "localnet")
    load_dotenv(dotenv_path=project_root / f".env.{network}")
    if network != "localnet":
        raise ValueError(f"Unsupported network for this script: {network}")

    parser = argparse.ArgumentParser(description="Deploy the ASA Metadata Registry on LocalNet")
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="Write METADATA_REGISTRY_APP_ID to .env.localnet",
    )
    args = parser.parse_args()

    return deploy(args.write_env)


if __name__ == "__main__":
    raise SystemExit(main())
