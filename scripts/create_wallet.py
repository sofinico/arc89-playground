from algokit_utils import AlgorandClient
from algosdk import mnemonic


def main() -> int:
    algorand_client = AlgorandClient.default_localnet()

    account_a = algorand_client.account.random()
    account_b = algorand_client.account.random()

    print("\n=== Account A ===")
    print(f"Address:  {account_a.address}")
    print(f"Mnemonic: {mnemonic.from_private_key(account_a.private_key)}")

    print("\n=== Account B ===")
    print(f"Address:  {account_b.address}")
    print(f"Mnemonic: {mnemonic.from_private_key(account_b.private_key)}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#
