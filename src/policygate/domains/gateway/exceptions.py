"""Domain exceptions for policy gateway flows."""


class PolicyGateError(Exception):
    """Base exception for gateway operations."""


class RouterValidationError(PolicyGateError):
    """Raised when router.yaml content is invalid."""


class RouterReferenceError(PolicyGateError):
    """Raised when requested aliases are missing in router.yaml."""


class RepositorySyncError(PolicyGateError):
    """Raised when repository sync cannot complete."""
