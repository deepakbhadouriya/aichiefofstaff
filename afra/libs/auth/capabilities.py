from collections.abc import Iterable


def require_capabilities(granted: Iterable[str], required: set[str]) -> bool:
    return required.issubset(set(granted))

