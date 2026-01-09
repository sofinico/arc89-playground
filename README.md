# ARC-89 vs ARC-90 Compliance

An ASA can be **ARC-89 compliant** without being **ARC-90 compliant** when it stores metadata in the ARC-89 registry format but doesn't use the ARC-90 URI scheme for reference. [1](#1-0) 

## Key Distinction

- **ARC-89 compliance**: Stores metadata in the registry's box-based format with proper hashing and structure
- **ARC-90 compliance**: Uses the `algorand://netauth/app/ID?box=` URI scheme to reference that metadata

## How It Works

The smart contract only enforces ARC-90 URI validation when the `IRR_FLG_ARC89_NATIVE` irreversible flag is set: [2](#1-1) 

```python
if self._is_arc89_native(asset_id):
    assert self._is_arc89_compliant(asset_id), err.ASA_NOT_ARC89_COMPLIANT
```

## Compliance Scenarios

1. **ARC-89 compliant, NOT ARC-90 compliant**:
   - Store metadata in the registry
   - Don't set the `IRR_FLG_ARC89_NATIVE` flag
   - Use any URL format (e.g., standard HTTPS)

2. **Both ARC-89 and ARC-90 compliant**:
   - Store metadata in the registry
   - Set the `IRR_FLG_ARC89_NATIVE` flag
   - Use ARC-90 URI format

This design allows flexibility where assets can benefit from on-chain metadata storage without being required to adopt the ARC-90 URI scheme. [3](#1-2) 

## Notes

The ARC-90 compliance check is optional and only enforced when explicitly requested via the ARC-89 native flag. This separation allows the registry to serve as a general metadata storage solution while providing enhanced URI-based discovery for assets that opt into it.

Wiki pages you might want to explore:
- [Development Guide (algorandfoundation/arc89)](/wiki/algorandfoundation/arc89#6)

### Citations

**File:** tests/smart_contract/test_arc89_create_metadata.py (L424-453)
```python
def test_fail_asa_not_arc89_compliant(
    asset_manager: SigningAccount,
    asa_metadata_registry_client: AsaMetadataRegistryClient,
    flags_arc89_native_and_arc3_compliant: MetadataFlags,
) -> None:
    # Create ASA without ARC89 compliant URL (not starting with arc90 partial URI)
    asset_id = asa_metadata_registry_client.algorand.send.asset_create(
        params=AssetCreateParams(
            sender=asset_manager.address,
            manager=asset_manager.address,
            total=42,
            asset_name="arc3",  # ARC3 compliant name
            url="https://example.com",  # NOT ARC89 compliant URL
        )
    ).asset_id

    # Try to create metadata with ARC89 native flag set
    metadata = AssetMetadata.from_json(
        asset_id=asset_id,
        json_obj=create_arc3_payload(name="Test"),
        flags=flags_arc89_native_and_arc3_compliant,
    )

    with pytest.raises(LogicError, match=err.ASA_NOT_ARC89_COMPLIANT):
        create_metadata(
            asset_manager=asset_manager,
            asa_metadata_registry_client=asa_metadata_registry_client,
            asset_id=asset_id,
            metadata=metadata,
        )
```
