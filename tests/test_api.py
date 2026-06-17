def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_application_returns_201_with_body(client):
    response = client.post(
        "/applications/",
        json={
            "company": "Acme Corp",
            "role_title": "Backend Engineer",
            "date_applied": "2026-01-05",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["company"] == "Acme Corp"
    assert body["status"] == "applied"
    assert body["follow_up_date"] == "2026-01-19"


def test_create_application_with_missing_field_returns_422(client):
    response = client.post("/applications/", json={"company": "Acme Corp"})
    assert response.status_code == 422


def test_get_unknown_application_returns_404(client):
    response = client.get("/applications/999")
    assert response.status_code == 404


def test_status_update_through_api(client):
    create_resp = client.post(
        "/applications/",
        json={
            "company": "Acme Corp",
            "role_title": "Backend Engineer",
            "date_applied": "2026-01-05",
        },
    )
    application_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/applications/{application_id}/status", json={"status": "interviewing"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "interviewing"


def test_invalid_status_jump_returns_409(client):
    create_resp = client.post(
        "/applications/",
        json={
            "company": "Acme Corp",
            "role_title": "Backend Engineer",
            "date_applied": "2026-01-05",
        },
    )
    application_id = create_resp.json()["id"]

    # applied -> offer is not a legal jump, must go through interviewing
    patch_resp = client.patch(
        f"/applications/{application_id}/status", json={"status": "offer"}
    )
    assert patch_resp.status_code == 409


def test_list_filters_by_status_query_param(client):
    client.post(
        "/applications/",
        json={"company": "Acme", "role_title": "Engineer", "date_applied": "2026-01-05"},
    )
    response = client.get("/applications/?status=offer")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_application_returns_204_then_404_on_refetch(client):
    create_resp = client.post(
        "/applications/",
        json={"company": "Acme", "role_title": "Engineer", "date_applied": "2026-01-05"},
    )
    application_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/applications/{application_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/applications/{application_id}")
    assert get_resp.status_code == 404
