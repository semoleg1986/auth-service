class DomainError(Exception):
    """Base error for domain layer."""


class InvariantViolationError(DomainError):
    """
    Raised when domain invariants are violated.

    :raises InvariantViolationError: Если нарушен доменный инвариант.
    """
