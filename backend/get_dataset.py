import logging
import spotipy
from flask import Flask, jsonify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import dotenv_values
import re
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import openai
import json
import ast
import datetime

def interpret_key(key_value):
    key_mappings = {0: 'C', 1: 'C#/Db', 2: 'D', 3: 'D#/Eb', 4: 'E', 5: 'F', 
                    6: 'F#/Gb', 7: 'G', 8: 'G#/Ab', 9: 'A', 10: 'A#/Bb', 11: 'B'}
    return key_mappings.get(key_value, "Key not found")

def test_playlist_ids():
    return ['37i9dQZF1EJAe7WqbEMeZ8', '37i9dQZF1EJuaJyiCXvjmU']

def interpret_mode(mode_value):
    mode_mappings = {0: 'Minor', 1: 'Major'}
    return mode_mappings.get(mode_value, "Mode not found")

def get_playlist_id(link_or_playlist_id):
    # Regular expression pattern to extract the playlist ID
    pattern = r"(?:playlist/|lists/|list=|taste-match/)([a-zA-Z0-9]+)"
    
    # Check if the input string is a URL or direct playlist ID
    is_url = link_or_playlist_id.startswith("https://open.spotify.com/")
    
    # Extract the playlist ID using regular expression
    if is_url:
        match = re.search(pattern, link_or_playlist_id)
    else:
        match = re.search(pattern, "https://open.spotify.com/playlist/" + link_or_playlist_id)
    
    if match:
        playlist_id = match.group(1)
        return playlist_id
    else:
        return None

def get_sample():
    sample = [
        { "id": 1, "event_ai": "R&B Night" },
        { "id": 2, "event_ai": "Afrobeats Party" },
        { "id": 3, "event_ai": "Bollywood Night" },
        { "id": 4, "event_ai": "R&B Night" },
        { "id": 5, "event_ai": "Pop Experience" },
        { "id": 6, "event_ai": "R&B Night" },
        { "id": 7, "event_ai": "Classical Soiree" },
        { "id": 8, "event_ai": "R&B Night" },
        { "id": 9, "event_ai": "Electronic Fusion" },
        { "id": 10, "event_ai": "R&B Night" },
        { "id": 11, "event_ai": "Soulful Sounds" },
        { "id": 12, "event_ai": "Big Band Swing" },
        { "id": 13, "event_ai": "Classical Soiree" },
        { "id": 14, "event_ai": "Indie Folk Festival" },
        { "id": 15, "event_ai": "Jazz Lounge" },
        { "id": 16, "event_ai": "Bollywood Night" },
        { "id": 17, "event_ai": "Bollywood Night" },
        { "id": 18, "event_ai": "Classical Performance" },
        { "id": 19, "event_ai": "Indie Folk Festival" },
        { "id": 20, "event_ai": "Indie Folk Festival" },
        { "id": 21, "event_ai": "Reggaeton Fiesta" },
        { "id": 22, "event_ai": "Indie Pop Showcase" },
        { "id": 23, "event_ai": "Acoustic Serenade" },
        { "id": 24, "event_ai": "Pop Experience" },
        { "id": 25, "event_ai": "R&B Night" },
        { "id": 26, "event_ai": "R&B Night" },
        { "id": 27, "event_ai": "Classical Soiree" },
        { "id": 28, "event_ai": "R&B Night" },
        { "id": 29, "event_ai": "Hip Hop Party" },
        { "id": 30, "event_ai": "R&B Night" },
        { "id": 31, "event_ai": "R&B Night" },
        { "id": 32, "event_ai": "R&B Night" },
        { "id": 33, "event_ai": "Reggaeton Fiesta" },
        { "id": 34, "event_ai": "Indie Pop Showcase" },
        { "id": 35, "event_ai": "Jazz Lounge" },
        { "id": 36, "event_ai": "Pop Experience" },
        { "id": 37, "event_ai": "EDM Extravaganza" },
        { "id": 38, "event_ai": "Jazz Lounge" },
        { "id": 39, "event_ai": "R&B Night" },
        { "id": 40, "event_ai": "Indie Folk Festival" },
        { "id": 41, "event_ai": "Jazz Lounge" },
        { "id": 42, "event_ai": "Indie Pop Showcase" },
        { "id": 43, "event_ai": "Bossa Nova Experience" },
        { "id": 44, "event_ai": "Pop Experience" },
        { "id": 45, "event_ai": "Classical Performance" },
        { "id": 46, "event_ai": "Bollywood Night" },
        { "id": 47, "event_ai": "Indie Pop Showcase" },
        { "id": 48, "event_ai": "R&B Night" },
        { "id": 49, "event_ai": "Acoustic Serenade" },
        { "id": 50, "event_ai": "R&B Night" }
        ]
    
    return sample

def chat(csv_data):
    query_1 = f""""You are an AI designed to provide the most insightful music that matches songs.
        
        Given the CSV data of various songs, where each row represents a song and columns represent specific features, including the song name, artist, genre etc. 
        
        Consider each song's cultural, geographical, genre, key, tone, popularity, and stylistic features to propose a set 10 to 25 'suitable themed music events' clusters for each song. 
        
        Group each song to the new proposed cluster and return an array of objects, each object should have only have 2 properties, the 'id' of the input id column and your suggested theme proposal 'event_ai' for each song. 
        
        Make sure that you don't return anything other than the array of objects, no text before or after and don't skip data. Also, make sure that the single or double quotes are consistent. Finally, do not abbreviate and provide the complete resopnse.
        
        
        """

    try:
        start_time = datetime.datetime.now()
        config = dotenv_values(".env")
        openai.api_key = config["OPENAI_API_KEY"]
        logging.info('Starting GPT API call via model')
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        #model="gpt-4"
        messages=[
            {"role": "system", "content": query_1},
            {"role": "user", "content": f"Here is the input csv: {csv_data}"}
            ]
        )
        clusters = response.choices[0].message['content']

        logging.info(f"Result of first query. Took: {datetime.datetime.now() - start_time}") 
        logging.info(clusters)
        logging.info("Fix possible bad format of string")
        clustes_format_fix = fix_incomplete_json_string(clusters)
        logging.info(clustes_format_fix)
        clustes_format_fix_quotes = fix_quote_inconsistency(clustes_format_fix)

    except:
        logging.error("Unable to get prompt response")

#     query_2 = f"""
# Return ONLY an object where each key is a cluster and the value is an array of objects representing the songs, 
# each object of the cluster array has song name and artist name.  Assign each song from {csv_data} to one of the clusters {clusters}. Return all the matches from the cluster. 

# For example: 
# {{"Indie Pop Night": [{{"artist_name": "Labrinth", "song": "Formula"}}]}}
# """

#     openai.api_key = config["OPENAI_API_KEY"]
#     response_2 = openai.ChatCompletion.create(
#       model="gpt-3.5-turbo-16k",
#       messages=[{"role": "user", "content": query_2}]
#     )
#     object_result = response_2.choices[0].message['content']
#     logging.info("Result of second query. Clusters: ")
#     logging.info(object_result)
    return clustes_format_fix_quotes

def fix_incomplete_json_string(input_str):
    if '...' in input_str:
        try:
            json.loads(input_str.replace('...', ''))  # Try to load without '...'
        except json.JSONDecodeError:
            incomplete_obj_start = input_str.rfind('{', 0, input_str.find('...'))
            incomplete_obj_end = input_str.find('}', incomplete_obj_start)
            while incomplete_obj_end < input_str.find('...') and incomplete_obj_end != -1:
                incomplete_obj_start = input_str.rfind('{', 0, incomplete_obj_start)
                incomplete_obj_end = input_str.find('}', incomplete_obj_start)

            if incomplete_obj_end == -1:
                input_str = input_str[:incomplete_obj_start] + input_str[incomplete_obj_start:].replace('...', '') + '}'
            else:
                input_str = input_str[:incomplete_obj_start] + input_str[incomplete_obj_start:incomplete_obj_end+1] + input_str[incomplete_obj_end+1:].replace('...', '')

            return fix_incomplete_json_string(input_str)  # Recursively check if there are more incomplete objects

    return input_str


def fix_quote_inconsistency(input_str):
    # Try to load the JSON with single quotes
    try:
        json.loads(input_str.replace("'", "\""))
        # If it works, replace all single quotes with double quotes
        return input_str.replace("'", "\"")
    except json.JSONDecodeError:
        # If it doesn't work, check if it works with double quotes
        try:
            json.loads(input_str)
            # If it works, replace only unescaped single quotes with double quotes
            return input_str.replace('\'', '\"')
        except json.JSONDecodeError:
            # If it doesn't work, there's another issue with the JSON
            print("The string is not valid JSON.")
            return input_str  

def get_groovy_events(link_or_playlist_id):

    return get_dataset(link_or_playlist_id, False)


def get_dataset(link_or_playlist_id, selected_groovy_event=False):
    try:
        playlist_id = get_playlist_id(link_or_playlist_id)

        # New or prepopulate dataset
        logging.info(playlist_id)
        logging.info(test_playlist_ids())
        logging.info(f"{playlist_id}" not in test_playlist_ids())
        create_new_dataset = f"{playlist_id}" not in test_playlist_ids()
        if (create_new_dataset):
            if playlist_id is None:
                logging.info('Invalid playlist ID or link.')
                return None

            logging.info(f'playlist ID extracted: {playlist_id}')
            config = dotenv_values(".env")
            client_id = config["CLIENT_ID"]
            client_secret = config["CLIENT_SECRET"]
            redirect_uri = config["REDIRECT_URI"]
            username = config["SPOTIFY_USERNAME"] 

            scope = "playlist-modify-public playlist-read-collaborative"

            # Create an OAuth object and assign it to the Spotify client
            auth_manager = SpotifyOAuth(client_id=client_id,
                                        client_secret=client_secret,
                                        redirect_uri=redirect_uri,
                                        username=username,
                                        scope=scope,
                                        show_dialog=True) # show_dialog will force a re-login, ensuring you get a fresh token

            sp = spotipy.Spotify(auth_manager=auth_manager)

            user_id = sp.me()['id']

            results = sp.playlist(playlist_id=playlist_id)
            tracks = results['tracks']['items']

            data = []

            logging.info('Extracting track data')
            start_time = datetime.datetime.now()
            for track in tracks:
                song_data = extract_song_data(track, sp)
                if song_data is not None:
                    data.append(song_data)

            logging.info(f'Finished extracting song data in {datetime.datetime.now() - start_time}')
            if data is not None:

                csv_file_name = f"{playlist_id}.csv"

                # Add an ID column to help shorten GPT response
                df = pd.DataFrame(data)
                df.insert(0, 'id', range(1, 1 + len(df)))
                data_to_csv(df, csv_file_name)

                # Return sample clusters
                clusters = chat(df)

                augment_csv(csv_file_name, clusters, csv_file_name)
                #data_to_csv(clusters, f'{playlist_id}-ai.csv')
                data_dict = build_cluster_dict(clusters, playlist_id)
                logging.info(data_dict)
                return data_dict
            else:
                return 'Please try again ...'
            
        # Prepopulated dataset
        else: 
            csv_file_name = f"{playlist_id}.csv"
            clusters = json.dumps(get_sample(), separators=(',', ':'))
            data_dict = build_cluster_dict(clusters, playlist_id)
            logging.info(data_dict)
            return data_dict

    except Exception as e:
        logging.info(f'Error occurred: {str(e)}')
        return jsonify({"Please try again ...": str(e)})

def build_cluster_dict(clusters, link_or_playlist_id):
    try:
        # Use json.loads to convert clusters string to a list
        clusters_list = json.loads(clusters)

        # Initialize an empty dictionary
        data_dict = {}

        # Iterate over each dictionary in the list
        for cluster_dict in clusters_list:
            # Use the 'event_ai' value as the key, and the 'song_name' as the value
            event_ai = cluster_dict['event_ai']
            song_id = cluster_dict['id']

            # If the event_ai is already a key in the data_dict, append the song_name
            if event_ai in data_dict:
                data_dict[event_ai].append(song_id)
            # Else, create a new key-value pair with the event_ai and a list containing the song_name
            else:
                data_dict[event_ai] = [song_id]

        # Add 'playlistID' to the dictionary
        data_dict['playlistID'] = link_or_playlist_id

        return data_dict
    except json.JSONDecodeError as e:
        logging.error(f"Error occurred while decoding JSON: {str(e)}")
        logging.error(f"Problematic JSON string: {clusters}")
        logging.error(f"Character causing error: {clusters[e.pos]}")
        return None

def extract_song_data(track, sp):
    song = track['track']['name']
    spotify_track_id = track['track']['id']
    song_popularity = track['track']['popularity']
    song_duration_ms = track['track']['duration_ms']
    artists = track['track']['artists']

    for artist in artists:
        artist_name = artist['name']
        artist_id = artist['id']

        artist_results = sp.artist(artist_id)
        artist_popularity = artist_results['popularity']
        genre = artist_results['genres']

        track_results = sp.audio_features(spotify_track_id)
        if track_results[0]:
            danceability = track_results[0]['danceability']
            energy = track_results[0]['energy']
            valence = track_results[0]['valence']
            acousticness = track_results[0]['acousticness']
            instrumentalness = track_results[0]['instrumentalness']
            speechiness = track_results[0]['speechiness']
            loudness = track_results[0]['loudness']
            tempo = track_results[0]['tempo']
            key = interpret_key(track_results[0]['key'])
            mode = interpret_mode(track_results[0]['mode'])
            time_signature = track_results[0]['time_signature']

            song_data = {
                'artist_name': artist_name,
                'artist_popularity': artist_popularity,
                'song': song,
                'song_popularity': song_popularity,
                'song_duration_ms': song_duration_ms,
                'spotify_track_id': spotify_track_id,
                'genre': genre,
                'danceability': danceability,
                'energy': energy,
                'valence': valence,
                'acousticness': acousticness,
                'instrumentalness': instrumentalness,
                'speechiness': speechiness,
                'loudness': loudness,
                'tempo': tempo,
                'key': key,
                'mode': mode,
                'time_signature': time_signature
            }

            return song_data

    return None


def print_song_info(song_data):
    logging.info(f'Artist: {song_data["artist_name"]}')
    logging.info(f'Artist Popularity: {song_data["artist_popularity"]}')
    logging.info(f'Song: {song_data["song"]}')
    logging.info(f'Song Popularity: {song_data["song_popularity"]}')
    logging.info(f'Song Duration (ms): {song_data["song_duration_ms"]}')
    logging.info(f'Spotify Track ID: {song_data["spotify_track_id"]}')
    logging.info(f'Genre: {song_data["genre"]}')
    logging.info(f'Danceability: {song_data["danceability"]}')
    logging.info(f'Energy: {song_data["energy"]}')
    logging.info(f'Valence: {song_data["valence"]}')
    logging.info(f'Acousticness: {song_data["acousticness"]}')
    logging.info(f'Instrumentalness: {song_data["instrumentalness"]}')
    logging.info(f'Speechiness: {song_data["speechiness"]}')
    logging.info(f'Loudness: {song_data["loudness"]}')
    logging.info(f'Tempo: {song_data["tempo"]}')
    logging.info(f'Key: {song_data["key"]}')
    logging.info(f'Mode: {song_data["mode"]}')
    logging.info(f'Time Signature: {song_data["time_signature"]}')
    logging.info('-----')


def print_summary(data):
    artist_list = [d['artist_name'] for d in data]
    song_list = [d['song'] for d in data]
    genre_list = [genre for d in data for genre in d['genre']]

    logging.info(f'Number of artists: {len(set(artist_list))}')
    logging.info(f'Number of songs: {len(set(song_list))}')
    logging.info(f'Number of genres: {len(set(genre_list))}')

    artist_counts = {artist: artist_list.count(artist) for artist in set(artist_list)}
    logging.info(f'Artist counts: {artist_counts}')

    song_counts = {song: song_list.count(song) for song in set(song_list)}
    logging.info(f'Song counts: {song_counts}')

    genre_counts = {genre: genre_list.count(genre) for genre in set(genre_list)}
    logging.info(f'Genre counts: {genre_counts}')

def data_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)


def augment_csv(data, clusters, new_csv_augmented_name):
    try:
        # Load CSV into pandas dataframe
        df = pd.read_csv(data)

         # Use ast.literal_eval to convert clusters string to a list
        clusters_list = ast.literal_eval(clusters)

        # Convert clusters list into a pandas dataframe
        clusters_df = pd.DataFrame(clusters_list)

        # Merge original dataframe with clusters dataframe
        df = pd.merge(df, clusters_df, how='left', left_on='id', right_on='id')

        # Drop the extra song_name column
        #df.drop('id', axis=1, inplace=True)

        # Replace NaN values in event_ai column with 'Not Classified'
        df['event_ai'].fillna('Not Classified', inplace=True)

        # Save the dataframe to a new CSV file
        df.to_csv(new_csv_augmented_name, index=False)
    except json.JSONDecodeError as e:
        logging.error(f"Error occurred while decoding JSON: {str(e)}")
        logging.error(f"Problematic JSON string: {clusters}")
        logging.error(f"Character causing error: {clusters[e.pos]}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return None


def event_dict_to_csv(event_dict, filename):
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(event_dict, orient='index')

    # Write the DataFrame to a CSV file
    df.to_csv(filename)


def get_event_array(grouped):
    # Extract the 'event' column from the grouped data
    event_array = grouped['event'].unique()
    
    # Convert numpy array to Python list
    event_list = event_array.tolist()
    
    # Convert numpy.nan (float) values to None
    event_list = [x if x==x else None for x in event_list]
    
    # Convert Python list to a dictionary to avoid issues with JSON serialization
    event_dict = {i: event for i, event in enumerate(event_list)}

    # Return the event dictionary
    logging.info(f'Returning event dict: {event_dict}')
    return event_dict
