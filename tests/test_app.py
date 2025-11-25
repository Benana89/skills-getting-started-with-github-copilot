import sys
from pathlib import Path
from urllib.parse import quote
import uuid

# Ensure src is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from app import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for a known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = f"test+{uuid.uuid4().hex}@example.com"

    signup_url = f"/activities/{quote(activity)}/signup"
    r = client.post(signup_url, params={"email": email})
    assert r.status_code == 200
    assert email in r.json().get("message", "")

    # Confirm participant present
    activities = client.get("/activities").json()
    participants = activities[activity]["participants"]
    assert email in participants

    # Duplicate signup should fail
    r2 = client.post(signup_url, params={"email": email})
    assert r2.status_code == 400

    # Unregister
    unregister_url = f"/activities/{quote(activity)}/unregister"
    ru = client.delete(unregister_url, params={"email": email})
    assert ru.status_code == 200

    # Confirm removal
    activities_after = client.get("/activities").json()
    assert email not in activities_after[activity]["participants"]
