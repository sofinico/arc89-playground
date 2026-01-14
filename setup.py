import logging
import os
from dataclasses import dataclass
from pathlib import Path

from algokit_utils import AlgoAmount, AlgorandClient, SigningAccount
from algosdk import account, mnemonic
from dotenv import load_dotenv

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global variables
algorand_client = None


# Configuration
@dataclass
class Config:
    """Configuration loaded from environment variables."""

    network: str
    arc90_netauth: str
    metadata_registry_app_id: int


# Utility functions
def _get_network() -> str:
    return os.getenv("NETWORK", "localnet").lower()


def _load_config() -> Config:
    """Load configuration from environment variables."""
    arc90_netauth = os.getenv("ARC90_NETAUTH")
    metadata_registry_app_id_str = os.getenv("METADATA_REGISTRY_APP_ID")
    
    if not arc90_netauth:
        raise ValueError("ARC90_NETAUTH environment variable is not set")
    if not metadata_registry_app_id_str:
        raise ValueError("METADATA_REGISTRY_APP_ID environment variable is not set")
    
    cfg = Config(
        network=_get_network(),
        arc90_netauth=arc90_netauth,
        metadata_registry_app_id=int(metadata_registry_app_id_str),
    )
    logger.info(cfg.__dict__)
    return cfg


# Load environment variables
project_root = Path(__file__).resolve().parent
load_dotenv(dotenv_path=project_root / ".env")
load_dotenv(dotenv_path=project_root / f".env.{_get_network()}")

# Initialize configuration
config = _load_config()


# Functions
def get_algorand_client() -> AlgorandClient:
    global algorand_client
    if algorand_client is None:
        algorand_client = AlgorandClient.from_environment()
    return algorand_client


def get_caller_address() -> str:
    caller_mnemonic = os.getenv("CALLER_MNEMONIC")
    if not caller_mnemonic:
        raise ValueError("CALLER_MNEMONIC environment variable is not set")
    private_key = mnemonic.to_private_key(caller_mnemonic)
    address: str = account.address_from_private_key(private_key)
    return address


def get_caller_signer() -> SigningAccount:
    caller_mnemonic = os.getenv("CALLER_MNEMONIC")
    private_key = mnemonic.to_private_key(caller_mnemonic)
    return SigningAccount(address=account.address_from_private_key(private_key), private_key=private_key)


# Main setup function
def setup_environment():
    """
    Setup and verify environment configuration.

    Caller:
    - For testnet, `CALLER_MNEMONIC` must be set in a `.env.testnet` file or exported in the shell.
    - For localnet, if `CALLER_MNEMONIC` is not set, a random account will be created.

    Funding:
    - For testnet, the account must be funded with ALGOs to cover transaction fees.
    - For localnet, the account will be automatically funded via the dispenser.

    Signer:
    - The signer is automatically added to the algorand client.
    """
    global algorand_client

    caller_mnemonic = os.getenv("CALLER_MNEMONIC")
    algorand_client = get_algorand_client()

    # Handle missing mnemonic
    if not caller_mnemonic:
        if config.network != "localnet":
            logger.warning("Set CALLER_MNEMONIC in a .env.testnet file or export it in your shell")
            raise ValueError("CALLER_MNEMONIC environment variable is not set")

        logger.info("CALLER_MNEMONIC not set - creating random account")
        random_account = algorand_client.account.random()
        logger.info(f"Created random account: {random_account.address}")
        os.environ["CALLER_MNEMONIC"] = mnemonic.from_private_key(random_account.private_key)
    else:
        logger.info("CALLER_MNEMONIC environment variable is set")

    # Fund account on localnet
    if config.network == "localnet":
        try:
            caller_address = get_caller_address()
            dispenser = algorand_client.account.localnet_dispenser()
            algorand_client.account.ensure_funded(caller_address, dispenser, AlgoAmount(algo=100))
            logger.info(f"Ensured account {caller_address} is funded")
        except Exception as e:
            logger.warning(f"Failed to setup dispenser or fund account: {e}")

    # Add signer to the algorand client
    algorand_client.account.set_signer(get_caller_address(), get_caller_signer().signer)


# Run setup on module import
setup_environment()
