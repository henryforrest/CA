import pytest
import os
import requests
from unittest.mock import patch, MagicMock
from audd import audd_app, AUDIO_DIR

@pytest.fixture
def client():
    """Flask test client setup."""
    audd_app.config["TESTING"] = True
    client = audd_app.test_client()
    yield client  # Run tests


# ================================================ HAPPY PATH =========================================================================

@patch("requests.post")
def test_identify_success(mock_post, client):
    """Test successful song identification and track addition.

    This test uses magic mock to fake the response from the audd API to test the the identify function works and 
    successfully adds the track to the database after identifying it. 

    It then asserts the response code and the output of the function with 200 and 'Track added to database' 
    
    """
    
    # Create a mock audio file
    filename = "test_song.wav"
    file_path = os.path.join(AUDIO_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(os.urandom(10))  # Dummy file data

    # Mock the response from the AudD API
    mock_audd_response = MagicMock()
    mock_audd_response.status_code = 200
    mock_audd_response.json.return_value = {
        "result": {"artist": "Olivia Rodrigo", "title": "good 4 u"}
    }
    mock_post.side_effect = lambda url, data=None, files=None, json=None: (
        mock_audd_response if "audd.io" in url else MagicMock(status_code=200)
    )

    # Send request
    response = client.post("/identify", json={"filename": filename})

    # Cleanup test file
    os.remove(file_path)

    assert response.status_code == 200
    assert response.json["artist"] == "Olivia Rodrigo"
    assert response.json["title"] == "good 4 u"
    assert response.json["message"] == "Track added to database"


# ================================================ UNHAPPY PATHS =========================================================================


def test_identify_no_filename(client):
    """Test identifying without providing a filename.
    
    This test ensures that the identify function correctly response with an error code when when the data input has no
    file name 

    asserts response code to 400 and output to 'No filename provided' 
    """
    response = client.post("/identify", json={})  # No filename
    assert response.status_code == 400
    assert response.json["error"] == "No filename provided"


def test_identify_file_not_found(client):
    """Test identifying a non-existent file.
    
    This test ensures that the identify function correctly response with an error code when a non existent filepath has been
    given as an input. 

    asserts response code to 404 as file not found and output to 'File not found'
    
    """
    response = client.post("/identify", json={"filename": "not a track.wav"})
    assert response.status_code == 404
    assert response.json["error"] == "File not found"


@patch("requests.post")
def test_identify_api_failure(mock_post, client):
    """Test handling failure in external API.
    
    Tests that the identify function correctly handles a failure of the audd API, uses magic mock to fake an API failure 
    to identify a track 

    asserts code to 500 and message to 'Failed to identify track'
    """
    # Create a mock audio file
    filename = "test_song.wav"
    file_path = os.path.join(AUDIO_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(os.urandom(10))  # Dummy file data

    # Mock API failure
    mock_post.return_value = MagicMock(status_code=500)

    response = client.post("/identify", json={"filename": filename})

    # Cleanup test file
    os.remove(file_path)

    assert response.status_code == 500
    assert response.json["error"] == "Failed to identify track"

