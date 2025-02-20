from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Set the database file path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "shamzam.db")

# Function to initialize the database
def init_db():
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

@app.route("/tracks", methods=['GET'])
def get_tracks():
    """ Function to output a list of all the tracks currently in the database 
    
    Does not take any JSON payload input 

    Expected output is 200 and a list of tracks in the database with the title, and id 
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, artist FROM tracks")
            tracks = cursor.fetchall()  # gather all the tracks from the database 
            track_list = [{"id": row[0], "title": row[1], "artist": row[2]} for row in tracks]  # loop through tracks 
        return jsonify(track_list)  # make the track list to a json format and return it 
    except Exception as e:
        return jsonify({"error": "Database error"}), 500


@app.route("/add_track", methods=['POST'])
def add_track():
    """ Function takes a json input of a track and adds it to the database 

    expected JSON payload: {"title": "good 4 u", "artist": "Olivia Rodrigo"}
    
    expected output is 200 and 'Track added!'
    """
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400  # makes sure the request is in JSON format 
    
    data = request.get_json()
    artist = data.get("artist")
    title = data.get("title")

    if not artist or not title:
        return jsonify({"error": "Missing title or artist"}), 400  # makes sure both title and artist are present 
    if not isinstance(artist, str) or not isinstance(title, str):
        return jsonify({"error": "'artist' and 'title' must be strings"}), 400  # makes sure title and artist are strings
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tracks WHERE title = ? AND artist = ?", (title, artist))
            existing_track = cursor.fetchone() #  check if the track already exists in the database 
            if existing_track:
                return jsonify({"error": "Track already exists"}), 409 # return error if track being added is already in database 
            
            cursor.execute("INSERT INTO tracks (title, artist) VALUES (?, ?)", (title, artist))
            conn.commit()
        return jsonify({"message": "Track added!", "track": {"title": title, "artist": artist}}), 200  # return success message with track info 
    except Exception as e:
        return jsonify({"error": "Database error"}), 500  # return error if database operation fails 


@app.route("/remove_track", methods=['POST'])
def remove_track():
    """ Function takes a json input of a track and removes it from the database 

    expected JSON payload: {"title": "good 4 u", "artist": "Olivia Rodrigo"}

    expected output is 200 and 'Track successfully removed.'
    """
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400  # makes sure the request is in JSON format 
    
    data = request.get_json()
    artist = data.get("artist")
    title = data.get("title")

    if not artist or not title:
        return jsonify({"error": "Missing title or artist"}), 400  # makes sure both title and artist are present 
    if not isinstance(artist, str) or not isinstance(title, str):
        return jsonify({"error": "'artist' and 'title' must be strings"}), 400   # makes sure title and artist are strings 
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tracks WHERE title = ? AND artist = ?", (title, artist))
            track = cursor.fetchone()  # check if the track exists in the database 
            if not track:
                return jsonify({"error": "Track not found"}), 404  # return error if track is not found 
            
            cursor.execute("DELETE FROM tracks WHERE title = ? AND artist = ?", (title, artist))
            conn.commit()
        return jsonify({"message": "Track successfully removed."}), 200  # return success message 
    except Exception as e:
        return jsonify({"error": "Error removing track from database"}), 500  # return error if database operation fails 


if __name__ == "__main__":
    init_db()
    print("Database initialized with tracks table!")
    app.run(debug=True)
