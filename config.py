import logging
import os
from dataclasses import dataclass
from pathlib import Path

from asa_metadata_registry import DEFAULT_DEPLOYMENTS

from utils.setup import LOCALNET_NETAUTH, load_env_files

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


def _get_deployment_config(network: str) -> tuple[str, int]:
    if network in DEFAULT_DEPLOYMENTS:
        deployment = DEFAULT_DEPLOYMENTS[network]
        if deployment.arc90_uri_netauth is None or deployment.app_id is None:
            raise ValueError(f"Incomplete deployment config for network: {network}")
        return deployment.arc90_uri_netauth, deployment.app_id

    if network == "localnet":
        metadata_registry_app_id_str = os.environ.get("METADATA_REGISTRY_APP_ID")
        if not metadata_registry_app_id_str:
            raise ValueError(
                "METADATA_REGISTRY_APP_ID must be set for localnet. Run `make setup`, which deploys a localnet registry and sets environment variable"
            )
        return LOCALNET_NETAUTH, int(metadata_registry_app_id_str)

    raise ValueError(f"Unsupported network: {network}")


def _load_config() -> Config:
    network, env_path = load_env_files(Path(__file__).resolve().parent)
    arc90_netauth, metadata_registry_app_id = _get_deployment_config(network)

    cfg = Config(
        network=network,
        arc90_netauth=arc90_netauth,
        metadata_registry_app_id=metadata_registry_app_id,
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
