class ApplicationError(Exception):
    """Base error for application layer."""


class NotFoundError(ApplicationError):
    """Raised when an aggregate is not found."""


class AccessDeniedError(ApplicationError):
    """Raised when policy denies the action."""


class InvariantViolationError(ApplicationError):
    """Raised when domain invariants are violated."""


class AuthenticationError(ApplicationError):
    """Raised when credentials are invalid."""


class ServiceConfigurationError(ApplicationError):
    """Raised when service runtime configuration is invalid."""

    def __init__(self, detail: str, *, status_code: int = 500) -> None:
        super().__init__(detail)
        self.status_code = status_code
