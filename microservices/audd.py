from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

audd_app = Flask(__name__)

db_url = "http://127.0.0.1:5000"  # set the port number that the database microservice runs on 


load_dotenv()  # load the API key from the .env file 

API = os.getenv('API_KEY')  # assign API key to correct variable 

AUDIO_DIR = os.path.join(os.getcwd()) # get current working directory to add to filename when identifying track 


@audd_app.route("/identify", methods=['POST'])
def identify():
    """ Function gets filename and send file of song snippet to audd API to get a song name and artist in return 
        
    expected JSON payload: { "filename": "good 4 u.wav"}

    expected output "Track added to database" 200 
    
    """
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400  # ensure that request input is a JSON format

    data = request.get_json()  # get data input 

    if 'filename' not in data:
        return jsonify({"error": "No filename provided"}), 400  # return error if data input format not right/no file name
    
    filename = data['filename']  # get the filename from the data input
    file_path = os.path.join(AUDIO_DIR, filename)  # get file path by adding current working directory to front of it 
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404   # output error if filepath does not exist 
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post('https://api.audd.io/', data={'api_token': API}, files=files)  #get response from API 
        
        if response.status_code == 200:  # assign all data if API response code is 200 ok 
            result = response.json()
            artist = result.get('result', {}).get('artist', 'Unknown')
            title = result.get('result', {}).get('title', 'Unknown')

            
            track_data = {"artist": artist, "title": title}
            add_response = requests.post(db_url + "/add_track", json=track_data)  # add track identified to the database 

            if add_response.status_code == 200:  # check if track was added to database correctly then return relevent html codes 
                return jsonify({"artist": artist, "title": title, "message": "Track added to database"}), 200
            else:
                return jsonify({"artist": artist, "title": title, "warning": "Track identified but could not be added"}), 500
        
        return jsonify({"error": "Failed to identify track"}), 500  # return error if API fails to identify the track correctly 

    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500



if __name__ == "__main__":
    with audd_app.app_context():
        print("Microservice started")
    
    # Start the microservice
    audd_app.run(debug=True, port=8080) # Runs on http://127.0.0.1:8080
