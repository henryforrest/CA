import pytest
from db import db_app, db

@pytest.fixture
def client():
    db_app.config["TESTING"] = True
    db_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory DB for tests
    with db_app.app_context():
        db.create_all()
    client = db_app.test_client()

    yield client  # Run tests

    with db_app.app_context():
        db.drop_all()  # Clean up DB after tests


# ============================================= HAPPY PATHS ==========================================================================


def test_add_track(client):
    """Test adding a track"""
    response = client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    assert response.status_code == 200
    assert response.json["message"] == "Track added!"

def test_remove_track(client):
    """Test removing a track"""
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.post("/remove_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    assert response.status_code == 200
    assert response.json["message"] == "Track <Track good 4 u by Olivia Rodrigo> by artist Olivia Rodrigo sucessfully removed."

def test_get_tracks(client):
    """Test retrieving tracks"""
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.get("/tracks")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "good 4 u"
    assert response.json[0]["artist"] == "Olivia Rodrigo"


# ============================================= UNHAPPY PATHS =======================================================================


def test_add_duplicate_track(client):
    """Test preventing duplicate track addition"""
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    assert response.status_code == 409
    assert response.json["error"] == "Track already exists"

def test_remove_nonexistent_track(client):
    """Test removing a track that does not exist"""
    response = client.post("/remove_track", json={"title": "nonexistent", "artist": "Unknown"})
    assert response.status_code == 404
    assert response.json["error"] == "Track not found"

def test_invalid_input(client):
    """Test adding a track with missing fields"""
    response = client.post("/add_track", json={"title": "good 4 u"})  # Missing artist
    assert response.status_code == 400
    assert response.json["error"] == "Missing title or artist"

