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
```

The `.env` file contains all configuration for both `localnet` and `testnet`. Each variable is suffixed with `_LOCALNET` or `_TESTNET`. Set the `NETWORK` variable to choose which configuration to use.

3. Run one-time setup (deploys registry on localnet and writes env values):

```bash
make setup
```

## Running Examples

### 1. Create an ASA (optional)

Create an ASA on the configured network. Set params in the [examples/create_asa.py](examples/create_asa.py) file.

```bash
make create-asa
```

To use an already created ASA, skip this step and set `ASSET_ID_LOCALNET` or `ASSET_ID_TESTNET` in your `.env` file, or export it directly:

```bash
export ASSET_ID=<your-asset-id>
```

### 2. Get ASA information

Fetch ASA details from the configured network.

```bash
make get-asa
```

### 3. Create metadata

Create ARC-89 metadata for an ASA. Set params in the [examples/create_metadata.py](examples/create_metadata.py) file.

```bash
make create-metadata
```

### 4. Get metadata

Fetch ARC-89 metadata for an ASA from the configured network.

```bash
make get-metadata
```

### 5. Delete metadata

Delete ARC-89 metadata for an ASA.

```bash
make delete-metadata
```

### 6. Delete ASA

Delete an ASA on the configured network.

```bash
make delete-asa
```

## FAQs

[WIP]

<details>
<summary>What is the ARC-89 Metadata Registry?</summary>
</details>

<details>
<summary>An already created ASA, can be ARC-89 compliant?</summary>
</details>

<details>
<summary>What is the difference between ARC-89 and ARC-90 compliance?</summary>
</details>

<details>
<summary>Can an ASA be ARC-3 and ARC-89 compliant?</summary>
</details>

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
