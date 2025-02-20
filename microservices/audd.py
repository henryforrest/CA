from flask import Flask, request, jsonify
import requests
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

audd_app = Flask(__name__)

db_url = "http://127.0.0.1:5000"


load_dotenv()

api_key = os.getenv('API_KEY')

AUDIO_DIR = os.path.join(os.getcwd()) 


@audd_app.route("/identify", methods=['POST'])
def identify():
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400

    data = request.get_json()

    if 'filename' not in data:
        return jsonify({"error": "No filename provided"}), 400
    
    filename = data['filename']
    file_path = os.path.join(AUDIO_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post('https://api.audd.io/', data={'api_token': API}, files=files)
        
        if response.status_code == 200:
            result = response.json()
            artist = result.get('result', {}).get('artist', 'Unknown')
            title = result.get('result', {}).get('title', 'Unknown')

            # Call the add_track function from another microservice
            track_data = {"artist": artist, "title": title}
            add_response = requests.post(db_url + "/add_track", json=track_data)

            if add_response.status_code == 200:
                return jsonify({"artist": artist, "title": title, "message": "Track added to database"}), 200
            else:
                return jsonify({"artist": artist, "title": title, "warning": "Track identified but could not be added"}), 500
        
        return jsonify({"error": "Failed to identify track"}), 500

    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500



if __name__ == "__main__":
    with audd_app.app_context():
        print("Microservice started")
    
    # Start the Flask microservice
    audd_app.run(debug=True, port=8080) # Runs on http://127.0.0.1:8080
