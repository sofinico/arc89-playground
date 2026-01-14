import os

from algokit_utils import AlgorandClient, SigningAccount
from algosdk import account, mnemonic

algorand_client = None


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
