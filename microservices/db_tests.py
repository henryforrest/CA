import pytest
import sqlite3
from db import app, DB_PATH

@pytest.fixture
def client():
    app.config["TESTING"] = True
    
    # Create a temporary in-memory database for testing
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL
            )
        """)
        conn.commit()
    
    client = app.test_client()
    yield client  # Run tests
    
    # Clean up database after tests
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks")
        conn.commit()

# ============================================= HAPPY PATHS ======================================================================

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
    assert response.json["message"] == "Track successfully removed."

def test_get_tracks(client):
    """Test retrieving tracks"""
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.get("/tracks")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "good 4 u"
    assert response.json[0]["artist"] == "Olivia Rodrigo"

# ============================================= UNHAPPY PATHS ===================================================================

def test_add_duplicate_track(client):
    """Test preventing duplicate track addition"""
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    assert response.status_code == 409
    assert response.json["error"] == "Track already exists"

def test_remove_nonexistent_track(client):
    """Test removing a track that does not exist"""
    response = client.post("/remove_track", json={"title": "not a track", "artist": "Unknown"})
    assert response.status_code == 404
    assert response.json["error"] == "Track not found"

def test_invalid_input_add(client):
    """Test adding a track with missing fields"""
    response = client.post("/add_track", json={"title": "good 4 u"})  # Missing artist
    assert response.status_code == 400
    assert response.json["error"] == "Missing title or artist"

def test_invalid_input_remove(client):
    """Test adding a track with missing fields"""
    response = client.post("/remove_track", json={"title": "good 4 u"})  # Missing artist
    assert response.status_code == 400
    assert response.json["error"] == "Missing title or artist"

def test_invalid_input_type_add(client):
    """Test adding a teack with non string type parameters """
    response = client.post("/add_track", json={"title": 4, "artist": "Olivia Rodrigo"})
    assert response.status_code == 400
    assert response.json["error"] == "'artist' and 'title' must be strings"

def test_invalid_input_type_remove(client):
    """Test adding a teack with non string type parameters """
    response = client.post("/remove_track", json={"title": "good 4 u", "artist": 4})
    assert response.status_code == 400
    assert response.json["error"] == "'artist' and 'title' must be strings"