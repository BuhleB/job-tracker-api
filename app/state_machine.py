"""
Business rules for application status transitions.

Kept free of any DB/FastAPI imports on purpose: this is the core domain
logic of the project, and it should be testable with plain unit tests
that run in milliseconds with no fixtures.
"""
from enum import Enum


class Status(str, Enum):
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Map of current status -> set of statuses it is legal to move to next.
# Anything not listed as a key is a terminal state (no outgoing moves).
ALLOWED_TRANSITIONS = {
    Status.APPLIED: {Status.INTERVIEWING, Status.REJECTED, Status.WITHDRAWN},
    Status.INTERVIEWING: {Status.OFFER, Status.REJECTED, Status.WITHDRAWN},
    Status.OFFER: {Status.ACCEPTED, Status.REJECTED, Status.WITHDRAWN},
}

TERMINAL_STATUSES = {Status.ACCEPTED, Status.REJECTED, Status.WITHDRAWN}


class InvalidTransitionError(ValueError):
    """Raised when a status change violates the allowed workflow."""


def validate_transition(current: Status, target: Status) -> None:
    """
    Raise InvalidTransitionError if moving from `current` to `target`
    is not a legal step in the application workflow.
    """
    if current == target:
        raise InvalidTransitionError(f"Application is already '{current.value}'.")

    if current in TERMINAL_STATUSES:
        raise InvalidTransitionError(
            f"'{current.value}' is a terminal status; it cannot be changed."
        )

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        allowed_names = ", ".join(s.value for s in allowed) or "none"
        raise InvalidTransitionError(
            f"Cannot move from '{current.value}' to '{target.value}'. "
            f"Allowed next steps: {allowed_names}."
        )


def default_follow_up_days(status: Status) -> int | None:
    """
    Suggested number of days until a follow-up, based on status.
    Returns None for terminal statuses, where a follow-up makes no sense.
    """
    if status in TERMINAL_STATUSES:
        return None
    return {
        Status.APPLIED: 14,
        Status.INTERVIEWING: 7,
        Status.OFFER: 3,
    }.get(status)
