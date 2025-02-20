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
    """Test adding a track
    
    ensures that the add track function is working and correctly adds a track to the database 

    asserts code to 200 and message to 'Track added!'
    """
    response = client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    assert response.status_code == 200
    assert response.json["message"] == "Track added!"

def test_remove_track(client):
    """Test removing a track
    
    ensures that the remove track function works correctly and removes the specified track 
    
    asserts code 200 and message is 'Track successfully removed."
    """
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.post("/remove_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    assert response.status_code == 200
    assert response.json["message"] == "Track successfully removed."

def test_get_tracks(client):
    """Test retrieving tracks
    
    ensures that the get track function correctly outputs the song previously added to the database 

    asserts code 200 and the output of the track 'good 4 u' by 'Olivia Rodrigo'    
    """
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.get("/tracks")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "good 4 u"
    assert response.json[0]["artist"] == "Olivia Rodrigo"

# ============================================= UNHAPPY PATHS ===================================================================

def test_add_duplicate_track(client):
    """Test preventing duplicate track addition
    
    ensures that the add track function correctly throws the error when a duplicate track is attempted to be added 
    
    asserts code 409 for conflict and message 'Track already exists'
    """
    client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    response = client.post("/add_track", json={"title": "good 4 u", "artist": "Olivia Rodrigo"})
    assert response.status_code == 409
    assert response.json["error"] == "Track already exists"

def test_remove_nonexistent_track(client):
    """Test removing a track that does not exist
    
    ensures that the remove track correctly throws the error when trying to remove a track that does not exist
    
    asserts code 404 for not found and message 'Track not found'
    """
    response = client.post("/remove_track", json={"title": "not a track", "artist": "Unknown"})
    assert response.status_code == 404
    assert response.json["error"] == "Track not found"

def test_invalid_input_add(client):
    """Test adding a track with missing fields
    
    ensures that the add track function correctly throws an error when trying to add a track without an artist
    
    asserts 400 for bad request and message 'Missing title or artist'
    """
    response = client.post("/add_track", json={"title": "good 4 u"})  # Missing artist
    assert response.status_code == 400
    assert response.json["error"] == "Missing title or artist"

def test_invalid_input_remove(client):
    """Test removing a track with missing fields
    
    ensures the remove track function correctly throws an error when trying to remove a track without an artist
    
    asserts 400 for bad request and message 'Missing title or artist'
    """
    response = client.post("/remove_track", json={"title": "good 4 u"})  # Missing artist
    assert response.status_code == 400
    assert response.json["error"] == "Missing title or artist"

def test_invalid_input_type_add(client):
    """Test adding a track with non string type parameters 
    
    ensures the add track function correctly throws and error when given an input that is not a string 
    
    asserts 400 for bad request and message "'artist' and 'title' must be strings"
    """
    response = client.post("/add_track", json={"title": 4, "artist": "Olivia Rodrigo"})
    assert response.status_code == 400
    assert response.json["error"] == "'artist' and 'title' must be strings"

def test_invalid_input_type_remove(client):
    """Test removing a track with non string type parameters 
    
    ensures the add track function correctly throws and error when given an input that is not a string 
    
    asserts 400 for bad request and message "'artist' and 'title' must be strings"
    """
    response = client.post("/remove_track", json={"title": "good 4 u", "artist": 4})
    assert response.status_code == 400
    assert response.json["error"] == "'artist' and 'title' must be strings"