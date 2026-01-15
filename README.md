# ARC-89 Playground

Playground for exploring the ARC-89 metadata registry on Algorand.

## Setup

1. Install dependencies:

```bash
poetry install
```

2. Copy environment configuration:

```bash
cp .env.example .env
cp .env.testnet.example .env.testnet
cp .env.localnet.example .env.localnet
```

`.env` is solely used for configuring the network (`testnet` or `localnet`). The configurations per network are stored in `.env.testnet` and `.env.localnet`.

3. Run one-time setup (deploys registry on localnet and writes env values):

```bash
make setup
```

## Running Examples

### 1. Create an ASA (optional)

Create an ASA on the configured network. Set params in the [examples/create_asa.py](examples/create_asa.py) file.

```bash
poetry run python -m examples.create_asa
```

To use an already created ASA, skip this step and set `ASSET_ID` env variable in the respective `.env.<network>` file or just:

```bash
export ASSET_ID=<your-asset-id>
```

## Developers

The repo uses pre-commit hooks to ensure code quality:

```bash
pre-commit install
```

To run the checks manually:

```bash
make lint
make format
make type-check
```
