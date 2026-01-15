import os

from algokit_utils import AlgorandClient, SigningAccount
from algosdk import account, mnemonic

# Singleton Algorand client
algorand_client = None

# Signer configured flag
_signer_configured = False


def get_algorand_client() -> AlgorandClient:
    global algorand_client
    if algorand_client is None:
        algorand_client = AlgorandClient.from_environment()
        _ensure_signer_configured()
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
    if not caller_mnemonic:
        raise ValueError("CALLER_MNEMONIC environment variable is not set")
    private_key = mnemonic.to_private_key(caller_mnemonic)
    return SigningAccount(address=account.address_from_private_key(private_key), private_key=private_key)


def _ensure_signer_configured() -> None:
    """Configure the caller signer on the singleton AlgorandClient instance."""
    global _signer_configured, algorand_client
    if _signer_configured:
        return

    assert algorand_client is not None, "AlgorandClient must be initialized before configuring signer"
    caller = get_caller_signer()
    algorand_client.account.set_signer(caller.address, caller.signer)
    _signer_configured = True
