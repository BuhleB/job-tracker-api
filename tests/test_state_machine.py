import pytest

from app.state_machine import (
    Status,
    InvalidTransitionError,
    validate_transition,
    default_follow_up_days,
)


class TestValidTransitions:
    def test_applied_to_interviewing_is_allowed(self):
        validate_transition(Status.APPLIED, Status.INTERVIEWING)  # no raise

    def test_interviewing_to_offer_is_allowed(self):
        validate_transition(Status.INTERVIEWING, Status.OFFER)

    def test_offer_to_accepted_is_allowed(self):
        validate_transition(Status.OFFER, Status.ACCEPTED)

    @pytest.mark.parametrize(
        "current", [Status.APPLIED, Status.INTERVIEWING, Status.OFFER]
    )
    def test_any_active_status_can_move_to_withdrawn(self, current):
        validate_transition(current, Status.WITHDRAWN)


class TestInvalidTransitions:
    def test_cannot_skip_interviewing_straight_to_offer(self):
        with pytest.raises(InvalidTransitionError):
            validate_transition(Status.APPLIED, Status.OFFER)

    def test_cannot_move_backwards(self):
        with pytest.raises(InvalidTransitionError):
            validate_transition(Status.INTERVIEWING, Status.APPLIED)

    @pytest.mark.parametrize(
        "terminal", [Status.ACCEPTED, Status.REJECTED, Status.WITHDRAWN]
    )
    def test_terminal_statuses_cannot_change(self, terminal):
        with pytest.raises(InvalidTransitionError):
            validate_transition(terminal, Status.APPLIED)

    def test_moving_to_same_status_is_rejected(self):
        with pytest.raises(InvalidTransitionError):
            validate_transition(Status.APPLIED, Status.APPLIED)


class TestFollowUpDefaults:
    def test_applied_suggests_two_week_follow_up(self):
        assert default_follow_up_days(Status.APPLIED) == 14

    def test_interviewing_suggests_one_week_follow_up(self):
        assert default_follow_up_days(Status.INTERVIEWING) == 7

    @pytest.mark.parametrize(
        "terminal", [Status.ACCEPTED, Status.REJECTED, Status.WITHDRAWN]
    )
    def test_terminal_statuses_have_no_follow_up(self, terminal):
        assert default_follow_up_days(terminal) is None
