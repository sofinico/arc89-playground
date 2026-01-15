import logging
import os
from dataclasses import dataclass
from pathlib import Path

from utils.setup import load_network_env

# Logging config
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# General config
_config = None


@dataclass
class Config:
    network: str
    arc90_netauth: str
    metadata_registry_app_id: int
    env_path: Path


def _load_config() -> Config:
    network, env_path = load_network_env(Path(__file__).resolve().parent)

    if not os.getenv("ARC90_NETAUTH"):
        raise ValueError("ARC90_NETAUTH environment variable is not set. Run `make setup` or set it in .env")
    if not os.getenv("METADATA_REGISTRY_APP_ID"):
        raise ValueError("METADATA_REGISTRY_APP_ID is not set. Run `make setup` or set it in .env")

    cfg = Config(
        network=network,
        arc90_netauth=os.environ["ARC90_NETAUTH"],
        metadata_registry_app_id=int(os.environ["METADATA_REGISTRY_APP_ID"]),
        env_path=env_path,
    )
    logger.info(f"Network: {cfg.network}")
    logger.info(f"Metadata Registry App ID: {cfg.metadata_registry_app_id}")
    return cfg


def get_config() -> Config:
    global _config
    if _config is None:
        _config = _load_config()
    return _config


if __name__ == "__main__":
    from utils.setup import main

    raise SystemExit(main())
else:
    # Load config for all imports except when running setup
    config = get_config()
