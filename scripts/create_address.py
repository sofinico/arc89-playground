from algokit_utils import AlgorandClient
from algosdk import mnemonic


def main() -> int:
    algorand_client = AlgorandClient.default_localnet()

    account = algorand_client.account.random()

    print("\n=== Account ===")
    print(f"Address:  {account.address}")
    print(f"Mnemonic: {mnemonic.from_private_key(account.private_key)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#
