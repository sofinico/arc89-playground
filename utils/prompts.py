from asa_metadata_registry import IrreversibleFlags, MetadataFlags, ReversibleFlags


def prompt_bool(label: str, default: bool) -> bool:
    default_hint = "Y/n" if default else "y/N"
    while True:
        response = input(f"{label} [{default_hint}]: ").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter y or n.")


def prompt_int(label: str, default: int | None) -> int:
    default_hint = f" [{default}]" if default is not None else ""
    while True:
        response = input(f"{label}{default_hint}: ").strip()
        if not response and default is not None:
            return default
        if not response:
            print("Please enter a value.")
            continue
        try:
            return int(response)
        except ValueError:
            print("Please enter a valid integer.")


def prompt_metadata_flags(
    default_reversible: ReversibleFlags, default_irreversible: IrreversibleFlags
) -> MetadataFlags:
    reversible = ReversibleFlags(
        arc20=prompt_bool("Reversible flag: ARC-20 compliance", default_reversible.arc20),
        arc62=prompt_bool("Reversible flag: ARC-62 compliance", default_reversible.arc62),
    )
    irreversible = IrreversibleFlags(
        arc3=prompt_bool("Irreversible flag: ARC-3 compliance", default_irreversible.arc3),
        arc89_native=prompt_bool(
            "Irreversible flag: ARC-89 native (requires ARC-90 URL prefix)",
            default_irreversible.arc89_native,
        ),
        immutable=prompt_bool("Irreversible flag: immutable metadata", default_irreversible.immutable),
    )
    return MetadataFlags(reversible=reversible, irreversible=irreversible)
