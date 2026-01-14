# ARC-89 Playground

Playground for exploring the ARC-89 metadata registry on Algorand.

## Quickstart

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

Run any example:

```bash
poetry run python examples/01_create_asa.py
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
