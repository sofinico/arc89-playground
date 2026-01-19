import sys
from pathlib import Path

from dotenv import set_key


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"localnet", "testnet"}:
        print("Usage: python scripts/switch_network.py <localnet|testnet>")
        return 1

    network = sys.argv[1]
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    set_key(env_path, "NETWORK", network, quote_mode="never")
    print(f"Set NETWORK={network} in {env_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
