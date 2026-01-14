import argparse
import logging
import os
from pathlib import Path

from algokit_utils import (
    AlgoAmount,
    AlgorandClient,
    AppClientCompilationParams,
    OnSchemaBreak,
    OnUpdate,
    OperationPerformed,
    PaymentParams,
    SigningAccount,
)
from asa_metadata_registry import Arc90Uri
from asa_metadata_registry import constants as const
from asa_metadata_registry._generated.asa_metadata_registry_client import (
    AsaMetadataRegistryFactory,
)
from dotenv import load_dotenv

TRUSTED_DEPLOYER = "TRUSTED_DEPLOYER"
ARC90_NETAUTH = "ARC90_NETAUTH"

logger = logging.getLogger(__name__)


def _load_env(network: str) -> None:
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(dotenv_path=project_root / ".env")
    load_dotenv(dotenv_path=project_root / f".env.{network}")


def _get_deployer(algorand_client: AlgorandClient, network: str) -> SigningAccount:
    try:
        deployer = algorand_client.account.from_environment("DEPLOYER")
        algorand_client.account.ensure_funded_from_environment(
            account_to_fund=deployer.address,
            min_spending_balance=AlgoAmount.from_algo(10),
        )
        return deployer
    except Exception:
        if network != "localnet":
            raise

    logger.info("DEPLOYER not configured; using a random localnet account")
    deployer = algorand_client.account.random()
    dispenser = algorand_client.account.localnet_dispenser()
    algorand_client.account.ensure_funded(deployer.address, dispenser, AlgoAmount.from_algo(10))
    return deployer


def _update_env_file(path: Path, key: str, value: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing env file: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    updated = False

    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            updated = True
            break

    if not updated:
        lines.append(f"{key}={value}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def deploy(network: str, write_env: bool) -> int:
    _load_env(network)
    netauth = os.environ.get(ARC90_NETAUTH)
    if not netauth:
        raise ValueError(f"{ARC90_NETAUTH} is not set")

    algorand = AlgorandClient.from_environment()
    algorand.set_default_validity_window(100)
    algorand.set_suggested_params_cache_timeout(0)

    deployer = _get_deployer(algorand, network)
    algorand.account.set_signer(deployer.address, deployer.signer)

    factory = algorand.client.get_typed_app_factory(
        AsaMetadataRegistryFactory,
        compilation_params=AppClientCompilationParams(
            deploy_time_params={
                TRUSTED_DEPLOYER: deployer.public_key,
                ARC90_NETAUTH: netauth,
            }
        ),
        default_sender=deployer.address,
        default_signer=deployer.signer,
    )

    app_client, result = factory.deploy(
        on_update=OnUpdate.AppendApp,
        on_schema_break=OnSchemaBreak.AppendApp,
    )

    if result.operation_performed in {
        OperationPerformed.Create,
        OperationPerformed.Replace,
    }:
        algorand.send.payment(
            PaymentParams(
                sender=deployer.address,
                receiver=app_client.app_address,
                amount=AlgoAmount(micro_algo=const.ACCOUNT_MBR),
            )
        )

    partial_uri = Arc90Uri(
        netauth=netauth,
        app_id=app_client.app_id,
        box_name=None,
    ).to_uri()

    logger.info("ASA Metadata Registry deployed")
    logger.info("App ID: %s", app_client.app_id)
    logger.info("App Address: %s", app_client.app_address)
    logger.info("ARC-90 Partial URI: %s", partial_uri)

    if write_env:
        env_path = Path(__file__).resolve().parent.parent / f".env.{network}"
        _update_env_file(env_path, "METADATA_REGISTRY_APP_ID", str(app_client.app_id))
        logger.info("Updated %s with METADATA_REGISTRY_APP_ID", env_path)

    return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Deploy the ASA Metadata Registry to localnet")
    parser.add_argument(
        "--network",
        default=os.getenv("NETWORK", "localnet"),
        help="Algorand network name (default: localnet)",
    )
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="Write METADATA_REGISTRY_APP_ID to .env.<network>",
    )
    args = parser.parse_args()

    return deploy(args.network.lower(), args.write_env)


if __name__ == "__main__":
    raise SystemExit(main())
