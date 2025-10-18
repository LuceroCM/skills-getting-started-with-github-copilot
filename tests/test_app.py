from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


def test_get_activities_contains_keys():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # should be a dict with known activities
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_cycle():
    activity = "Chess Club"
    email = "test_student@mergington.edu"

    # Ensure email not already present
    participants_before = [p.lower() for p in activities[activity]["participants"]]
    if email.lower() in participants_before:
        # if present, remove to ensure test isolation
        activities[activity]["participants"] = [p for p in activities[activity]["participants"] if p.lower() != email.lower()]

    # Signup
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify via GET that participant appears
    get_resp = client.get("/activities")
    assert get_resp.status_code == 200
    data = get_resp.json()
    participants = [p.lower() for p in data[activity]["participants"]]
    assert email.lower() in participants

    # Unregister
    delete_resp = client.delete(f"/activities/{activity}/participants", json={"email": email})
    assert delete_resp.status_code == 200
    assert "Unregistered" in delete_resp.json().get("message", "")

    # Verify removed
    get_resp2 = client.get("/activities")
    data2 = get_resp2.json()
    participants2 = [p.lower() for p in data2[activity]["participants"]]
    assert email.lower() not in participants2
