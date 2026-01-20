# ARC-89 Playground

Playground for exploring the ARC-89 metadata registry on Algorand.

## Setup

1. Install dependencies:

```bash
poetry install
```

2. Copy environment configuration:

```bash
make env-files
```

3. Set the network to use:

```bash
make use-localnet # or
make use-testnet
```

Switch between networks with these commands. These set the `NETWORK` environment variable, which can also be manually set in the `.env` or override it per command, e.g. `NETWORK=testnet make create-asa`.

> [!IMPORTANT]\
> For testnet, ensure the `CALLER_MNEMONIC` environment variable is available and funded (`export CALLER_MNEMONIC=...` or set in `.env.testnet`).
> Create a new address with `make new-address` and fund it here https://lora.algokit.io/testnet/fund.

4. Run setup (required first time or after switching networks):

```bash
make setup
```

## Running Examples

### 1. Create an ASA (optional)

Create an ASA on the configured network. Set params in the [examples/create_asa.py](examples/create_asa.py) file.

```bash
make create-asa
```

To use an already created ASA, skip this step and set `ASSET_ID` in your `.env.localnet` or `.env.testnet` file, or export it directly:

```bash
export ASSET_ID=<your-asset-id>
```

### 2. Get ASA information

Fetch ASA details from the configured network.

```bash
make get-asa
```

### 3. Create metadata

Create ARC-89 metadata for an ASA. You will be prompted for the ASA parameters in the CLI. Metadata JSON defaults to `metadata/example.json` (override with `METADATA_JSON_PATH` or `--metadata-json`).

```bash
make create-metadata
```

Non-interactive:

```bash
poetry run python -m examples.create_metadata --no-prompt --asset-id <asset-id> --metadata-json path/to/metadata.json
```

Non-interactive runs require `--asset-id` or `ASSET_ID` env var and use the default metadata flags unless you edit the defaults in `examples/create_metadata.py`.

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

<details>
<summary>What is the ARC-89 ASA Metadata Registry?</summary><br>
The ASA Metadata Registry is a singleton smart contract application that provides on-chain JSON metadata storage for Algorand Standard Assets (ASAs), implementing the [ARC-89 specification](https://dev.algorand.co/arc-standards/arc-0089).

There is exactly one storage box per ASA, addressable by Asset ID. The Asset Metadata Box is readable via Algod API (ledger queries) or the AVM (intra-app calls).

</details>

<details>
<summary>Who has the metadata authority?</summary><br>

ARC-89 aligns metadata authority with the [**ASA Manager**](https://dev.algorand.co/concepts/assets/overview/#mutable-asset-parameters) role, who can:

- Create/update/delete metadata
- Toggle flags
- Lock metadata as immutable
- Migrate metadata to future registries

NOTE: The ASA Manager Address MUST NOT be set to the Zero Address on creation. If the ASA Manager Address is set to the Zero Address after metadata creation, this implies the metadata is _immutable_, regardless of the [Metadata Immutability](https://dev.algorand.co/arc-standards/arc-0089/#metadata-immutability) flag.

</details>

<details>
<summary>How is the Asset Metadata Box structured?</summary><br>

[**Header**](https://dev.algorand.co/arc-standards/arc-0089/#metadata-header) Encodes additional attributes of the Asset Metadata.

- Metadata Identifiers
- Reversible Flags
- Irreversible Flags
- Metadata Hash
- Last Modified Round
- Deprecated By

[**Body**](https://dev.algorand.co/arc-standards/arc-0089/#metadata) The actual metadata JSON.

</details>

<details>
<summary>Can an existing ASA become ARC-89 compliant?</summary><br>

Yes! An ASA created before the ARC-89 standard can become ARC-89 compliant by adding metadata to it through the ASA Metadata Registry. So **[backwards compatibility](https://dev.algorand.co/arc-standards/arc-0089/#backwards-compatibility) for existing ASAs is possible**.

However, since the Asset URL (`au`) field is immutable, an existing (pre-ARC-89) ASA with a non-ARC-90 URL can never become ARC-90 compliant. It can only be ARC-90/ARC-89-native if its current URL already starts with the ARC-89 partial ARC-90 URI:
`algorand://<netauth>/app/<singleton_arc89_app_id>?box=`
(optionally with a compliance fragment like `#arc<A>+<B>+<C>...`).

As for the current registry implementation, attempting to create flagged ARC-89 native metadata on ASAs with non-compliant URLs [will fail](https://github.com/algorandfoundation/arc89/blob/main/tests/smart_contract/test_arc89_create_metadata.py#L411).

</details>

<details>
<summary>What is the difference between ARC-89 and ARC-90 compliance?</summary><br>

ARC-89 is the metadata registry standard that defines how JSON metadata is stored on-chain in smart contract boxes, while ARC-90 is the URI scheme that provides a unified Algorand URI scheme which can be used to reference on-chain resources in general, and metadata in particular.

Compliance scenarios:

1. **ARC-89 compliant, NOT ARC-90 compliant**:

   - Store metadata in the registry
   - Do not set the `IRR_FLG_ARC89_NATIVE` flag
   - Use any URL format (e.g., standard HTTPS)

This can be the case of ASAs created before the ARC-89 standard.

2. **Both ARC-89 and ARC-90 compliant**:

   - Store metadata in the registry
   - Set the `IRR_FLG_ARC89_NATIVE` flag
   - Set URL (`au`) to the ARC-89 partial ARC-90 URI for the registry app (clients resolve the full ARC-90 Asset Metadata URI by adding the asset id box name)

Current registry implementation validates the required partial-URI prefix when the `IRR_FLG_ARC89_NATIVE` irreversible flag is set; the ARC-90 compliance fragment is optional.

</details>

<details>
<summary>Can an ASA be ARC-3 and ARC-89 compliant?</summary><br>

Yes, an ASA can be both ARC-3 and ARC-89 compliant simultaneously. This dual compliance allows an ASA to benefit from both NFT metadata standards (ARC-3) and on-chain metadata storage (ARC-89).

Since ARC-3 uses its own hash convention, if the metadata is flagged as ARC-3 and as ARC-89, the hash check is bypassed on metadata creation.

ARC-90 fragment special case: when declaring ARC-3 compliance, the fragment MUST be exactly `#arc3` with no additional ARC identifiers.

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
