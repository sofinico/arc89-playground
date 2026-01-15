import logging
import os
from pathlib import Path

from algokit_utils import AlgoAmount, AlgorandClient, AppClientCompilationParams, PaymentParams
from algosdk import account, mnemonic
from asa_metadata_registry import DEFAULT_DEPLOYMENTS, Arc90Uri
from asa_metadata_registry import constants as registry_constants
from asa_metadata_registry._generated.asa_metadata_registry_client import AsaMetadataRegistryFactory
from dotenv import load_dotenv, set_key

logger = logging.getLogger(__name__)

# Environment variable names that have network-specific suffixes
_NETWORK_SPECIFIC_VARS = (
    "ALGOD_SERVER",
    "ALGOD_PORT",
    "ALGOD_TOKEN",
    "INDEXER_SERVER",
    "INDEXER_PORT",
    "INDEXER_TOKEN",
    "ARC90_NETAUTH",
    "METADATA_REGISTRY_APP_ID",
    "CALLER_MNEMONIC",
    "ASSET_ID",
)


# Environment helpers
def get_network() -> str:
    """Get the configured network from environment.

    Returns:
        Network name ('localnet' or 'testnet')

    Raises:
        ValueError: If NETWORK is not set to a valid value
    """
    network = os.getenv("NETWORK", "localnet").lower()
    if network not in ("localnet", "testnet"):
        raise ValueError(f"NETWORK must be 'localnet' or 'testnet', got: {network}")
    return network


def _map_network_variables(network: str) -> None:
    """Map network-specific suffixed variables to their base names.

    For example, if network is 'localnet', maps ALGOD_SERVER_LOCALNET -> ALGOD_SERVER.

    Args:
        network: The network name ('localnet' or 'testnet')
    """
    suffix = f"_{network.upper()}"

    for var_name in _NETWORK_SPECIFIC_VARS:
        suffixed_var = f"{var_name}{suffix}"
        value = os.getenv(suffixed_var)
        if value is not None:
            os.environ[var_name] = value


def load_network_env(project_root: Path) -> tuple[str, Path]:
    """Load environment configuration and map network-specific variables.

    Loads the .env file and maps network-specific variables (suffixed with
    _LOCALNET or _TESTNET) to their base names based on the NETWORK setting.

    Args:
        project_root: Root directory of the project containing .env file

    Returns:
        Tuple of (network_name, env_file_path)

    Raises:
        ValueError: If NETWORK is not set to a valid value
    """
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path)
    network = get_network()
    _map_network_variables(network)
    return network, env_path


# Setup CLI helpers
def _deploy_localnet_registry(algorand: AlgorandClient) -> int:
    if not os.getenv("ARC90_NETAUTH"):
        raise ValueError("ARC90_NETAUTH environment variable is not set")

    deployer = algorand.account.random()
    dispenser = algorand.account.localnet_dispenser()
    algorand.account.ensure_funded(deployer.address, dispenser, AlgoAmount.from_algo(10))
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
            amount=AlgoAmount(micro_algo=registry_constants.ACCOUNT_MBR),
        )
    )

    partial_uri = Arc90Uri(netauth=os.environ["ARC90_NETAUTH"], app_id=app_client.app_id, box_name=None).to_uri()
    logger.info("ASA Metadata Registry deployed (app_id=%s)", app_client.app_id)
    logger.info("ARC-90 partial URI: %s", partial_uri)
    return app_client.app_id


def _ensure_registry_app_id(algorand: AlgorandClient, env_path: Path, network: str) -> int:
    # Localnet: check existing app id or deploy new
    if network == "localnet":
        app_id_str = os.getenv("METADATA_REGISTRY_APP_ID")
        if app_id_str:
            app_id = int(app_id_str)
            try:
                algorand.client.algod.application_info(app_id)
                logger.info("METADATA_REGISTRY_APP_ID already set to %s", app_id)
                return app_id
            except Exception:
                logger.info("Existing METADATA_REGISTRY_APP_ID is not valid on localnet; redeploying")
        app_id = _deploy_localnet_registry(algorand)
        set_key(env_path, f"METADATA_REGISTRY_APP_ID_{network.upper()}", str(app_id), quote_mode="never")
        return app_id

    # Testnet: use default deployment without persisting to .env.
    default_app_id = DEFAULT_DEPLOYMENTS[network].app_id
    if default_app_id is None:
        raise ValueError(f"No default registry deployment found for {network}")
    app_id = int(default_app_id)
    os.environ["METADATA_REGISTRY_APP_ID"] = str(app_id)
    logger.info("Using default registry app id for %s: %s", network, app_id)
    return app_id


def _ensure_caller_mnemonic(algorand: AlgorandClient, network: str, env_path: Path) -> str:
    caller_mnemonic = os.getenv("CALLER_MNEMONIC")
    if caller_mnemonic:
        logger.info("CALLER_MNEMONIC already set")
        return caller_mnemonic
    if network != "localnet":
        raise ValueError(
            f"CALLER_MNEMONIC is not set. Set CALLER_MNEMONIC_{network.upper()} in .env or export it in your shell."
        )

    random_account = algorand.account.random()
    caller_mnemonic = str(mnemonic.from_private_key(random_account.private_key))
    set_key(env_path, f"CALLER_MNEMONIC_{network.upper()}", caller_mnemonic, quote_mode="never")
    logger.info("Generated localnet caller account: %s", random_account.address)
    return caller_mnemonic


def _ensure_localnet_funding(algorand: AlgorandClient, caller_mnemonic: str) -> None:
    private_key = mnemonic.to_private_key(caller_mnemonic)
    caller_address = account.address_from_private_key(private_key)
    dispenser = algorand.account.localnet_dispenser()
    algorand.account.ensure_funded(caller_address, dispenser, AlgoAmount(algo=100))
    logger.info("Ensured account %s is funded", caller_address)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    network, env_path = load_network_env(Path(__file__).resolve().parent.parent)
    algorand = AlgorandClient.from_environment()
    logger.info("Network: %s", network)

    _ensure_registry_app_id(algorand, env_path, network)
    caller_mnemonic = _ensure_caller_mnemonic(algorand, network, env_path)
    if network == "localnet":
        _ensure_localnet_funding(algorand, caller_mnemonic)

    logger.info("Setup complete for %s", network)
    return 0
