import os
import tempfile

os.environ["KP_DB_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "t.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_flow():
    c = TestClient(app)
    assert c.get("/api/auth/status").json() == {"has_user": False}
    t = c.post("/api/auth/setup", json={"username": "me", "password": "secret123"}).json()["token"]
    assert c.post("/api/auth/setup", json={"username": "x", "password": "secret123"}).status_code == 400
    H = {"Authorization": "Bearer " + t}
    assert c.get("/api/charts").status_code == 401
    ch = c.post("/api/charts", json={"name": "N", "birth_local": "1931-10-10T13:11:00", "tz": "+05:30",
                                     "lat": 13.07, "lon": 80.25}, headers=H).json()
    c.post(f"/api/charts/{ch['id']}/events", json={"matter_key": "marriage", "date": "1950-09-01"}, headers=H)
    for aya in ("KSK", "Lahiri"):
        assert c.get(f"/api/charts/{ch['id']}/chart?ayanamsa={aya}", headers=H).status_code == 200
    b = c.get(f"/api/charts/{ch['id']}/bio?matter=marriage", headers=H).json()
    assert b["matters"][0]["variants"][0]["known_event_check"]["date"] == "1950-09-01"
    h = c.post("/api/horary", json={"matter_key": "job", "number": 100, "lat": 13.07, "lon": 80.25}, headers=H)
    assert h.status_code == 200
    r = c.post("/api/rectify", json={"date": "1935-11-21", "time_from": "05:00", "time_to": "05:40", "tz": "+05:30",
                                     "lat": 31.32, "lon": 75.3, "judge_utc": "1966-09-02T12:32:00",
                                     "judge_lat": 28.63, "judge_lon": 77.22}, headers=H)
    assert r.status_code == 200
