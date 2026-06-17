from datetime import date

from app import crud, schemas
from app.state_machine import Status


def make_application(db_session, company="Acme Corp", role_title="Backend Engineer"):
    payload = schemas.ApplicationCreate(
        company=company,
        role_title=role_title,
        date_applied=date(2026, 1, 5),
    )
    return crud.create_application(db_session, payload)


class TestCreateApplication:
    def test_new_application_defaults_to_applied_status(self, db_session):
        app_obj = make_application(db_session)
        assert app_obj.status == Status.APPLIED

    def test_follow_up_date_is_auto_calculated(self, db_session):
        app_obj = make_application(db_session)
        assert app_obj.follow_up_date == date(2026, 1, 19)  # +14 days


class TestListApplications:
    def test_list_returns_all_by_default(self, db_session):
        make_application(db_session, company="Acme Corp")
        make_application(db_session, company="Globex")
        results = crud.list_applications(db_session)
        assert len(results) == 2

    def test_list_can_filter_by_status(self, db_session):
        make_application(db_session, company="Acme Corp")
        results = crud.list_applications(db_session, status=Status.OFFER)
        assert results == []


class TestUpdateStatus:
    def test_valid_transition_updates_status_and_follow_up(self, db_session):
        app_obj = make_application(db_session)
        updated = crud.update_status(db_session, app_obj, Status.INTERVIEWING)
        assert updated.status == Status.INTERVIEWING
        assert updated.follow_up_date == date(2026, 1, 12)  # +7 days

    def test_reaching_terminal_status_clears_follow_up(self, db_session):
        app_obj = make_application(db_session)
        updated = crud.update_status(db_session, app_obj, Status.REJECTED)
        assert updated.follow_up_date is None


class TestDeleteApplication:
    def test_delete_removes_record(self, db_session):
        app_obj = make_application(db_session)
        crud.delete_application(db_session, app_obj)
        assert crud.get_application(db_session, app_obj.id) is None
