import copy
import urllib.parse
import pytest
from fastapi.testclient import TestClient

import src.app as app_module

# Arrange: keep a pristine copy of the in-memory activities and restore before each test
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    yield

client = TestClient(app_module.app)


def test_get_activities():
    # Arrange
    activity_name = "Chess Club"

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert activity_name in data
    assert isinstance(data[activity_name]["participants"], list)


def test_signup():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{urllib.parse.quote(activity)}/signup"

    # Act
    resp = client.post(url, params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]
    assert resp.json().get("message") == f"Signed up {email} for {activity}"


def test_duplicate_signup():
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]
    url = f"/activities/{urllib.parse.quote(activity)}/signup"

    # Act
    resp = client.post(url, params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "").lower()


def test_remove_participant():
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]
    url = f"/activities/{urllib.parse.quote(activity)}/signup"

    # Act
    resp = client.delete(url, params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]
    assert resp.json().get("message") == f"Removed {email} from {activity}"
