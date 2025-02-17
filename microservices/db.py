from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy, SQLAlchemyError
import os
from datetime import datetime

db_app = Flask(__name__)

# Set the database file path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'shamzam.db')}"
db_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(db_app)

# Define the Track model
class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)


    def __repr__(self):
        return f"<Track {self.title} by {self.artist}>"
    


@db_app.route("/tracks", methods=['GET'])
def tracks():
    with db_app.app_context():
        try:
            tracks = Track.query.all()
            track_list = [{"id": track.id, "title": track.title, "artist": track.artist} for track in tracks]
            return jsonify(track_list)
        except SQLAlchemyError as e:
            return jsonify({"error": "Database error"}), 500


@db_app.route("/add_track", methods=['POST'])
def add_track():
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.get_json()
    artist = data.get("artist")
    title = data.get("title")

    if not artist or not title:
        return jsonify({"error": "Missing title or artist"}), 400
    if not isinstance(artist, str) or not isinstance(title, str):
        return jsonify({"error": "'artist' and 'title' must be strings"}), 400
    
    # Check if track already exists
    existing_track = Track.query.filter_by(title=title, artist=artist).first()
    if existing_track:
        return jsonify({"error": "Track already exists"}), 409
    
    new_track = Track(title=title, artist=artist)
    db.session.add(new_track)
    db.session.commit()

    return jsonify({"message": "Track added!", "track": {"title": new_track.title, "artist": new_track.artist}})



@db_app.route("/remove_track", methods=['POST'])
def remove_track():
    data = request.get_json()


    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    artist = data.get("artist")
    title = data.get("title")

    if not artist or not title:
        return jsonify({"error": "Missing 'artist' or 'title' field"}), 400
    if not isinstance(artist, str) or not isinstance(title, str):
        return jsonify({"error": "'artist' and 'title' must be strings"}), 400

    with db_app.app_context():
        try:
            track = db.session.execute(
                db.select(Track).filter_by(artist=artist, title=title)
            ).scalar_one_or_none()

            if not track:
                return jsonify({"error": "Track not found"}), 404
            
            db.session.delete(track)
            db.session.commit()

            return jsonify({"message": f'Track {track} by artist {artist} sucessfully removed.'}), 200
        except Exception as e: # come back exception name 
            return jsonify({"error": "Error removing track from database"}), 500




# Initialise the database
if __name__ == "__main__":
    with db_app.app_context():
        db.create_all()
        print("Database initialised with tracks table!")

    db_app.run(debug=True)  # Runs on http://127.0.0.1:5000 by default
