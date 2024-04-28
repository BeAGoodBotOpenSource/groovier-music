from flask import Flask, jsonify, request
import modify_playlist as mp
import get_dataset as gd
from flask_cors import CORS, cross_origin
import logging

# set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
CORS(app, origins=[
   'http://localhost:3000', 
   'http://localhost:8000',
   'https://groovy-music.onrender.com',
   'https://groovy-music-backend.onrender.com',
   'http://groovy-music.onrender.com',
   'http://35.160.120.126',
   'http://44.233.151.27',
   'http://34.211.200.85'])

@app.route('/', methods=["GET"])
def verify_connection():
  response = jsonify({"msg": "Connected!"})
  return response, 200

@app.route('/create-playlist', methods=["POST"])
@cross_origin()
def create_playlist():
    data = request.get_json()
    playlistID = data.get('blendLink')  # Get blendLink from request
    genre = data.get('genre')  # Get genre from request

    if playlistID is not None and genre is not None:
        logging.info('Creating playlist')
        playlist = mp.create_event_playlist(genre, playlistID)
        return playlist, 200
    else:
        # TODO: implement better error handling with correct http response
        raise ValueError 
      
    return response, 200
  

@app.route('/get-groovy-events', methods=["POST"])
@cross_origin()
def get_grovy_events():
  #Skipping validation for now
  logging.info('In 5 get-groovy-events')
  data = request.get_json()
  blend_link = data.get('blendLink')
  
  if (blend_link is not None):
    logging.info(f'Blended link passed successefuly: {blend_link}')
  else:
    logging.info('Skippin validation for now')
      
  link_or_playlist_id = blend_link or 'https://open.spotify.com/playlist/37i9dQZF1EJuaJyiCXvjmU?si=5ce770ccf48e4319'
  try: 
    response = gd.get_groovy_events(link_or_playlist_id)
    logging.info('returning response')
    logging.info(response)
    return response, 200
  except:
    raise ValueError

  return response, 200

if __name__ == '__main__':
  app.run(debug=True)
