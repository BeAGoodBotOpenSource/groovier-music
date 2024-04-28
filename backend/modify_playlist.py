import logging
from spotipy.oauth2 import SpotifyOAuth
from dotenv import dotenv_values
import spotipy
import pandas as pd
import get_dataset as gd
import traceback

# Example script to expand playlist
#    df = pd.read_csv('cluster_names.csv')
 #   selection = make_mock_selection(df, event_selection)
#
 #   expand_blend(selection, str(event_selection), "Description")
#
# "    playlist = sp.user_playlist_create(user_id, event_selection, description=event_selection)

#     df = pd.read_csv('cluster_names.csv')
#     selection = make_mock_selection(df, event_selection)
#     expand_blend(selection, "New Playlist", "Description")

#     return playlist"


def add_songs_to_playlist(sp, songs, playlist):
    """add specified collection of songs given as a list of track_id
    in the form of ['spotify:track:{track_id1}', 'spotify:track:{track_id2}', ... ]
    to playlist given by a playlist id

    Args:
        songs (list): list of track_ids in the form of ['spotify:track:{track_id1}', 'spotify:track:{track_id2}', ... ]
        playlist (string): playlist id
    """
    sp.playlist_add_items(songs, playlist)
    
    
def get_top_five_selected_tracks(dataframe, event):
    # subset the dataframe based on event
    df_subset = dataframe[dataframe['event_ai'] == event]

    # sort the subset dataframe by song popularity in descending order
    df_subset = df_subset.sort_values(by='song_popularity', ascending=False)

    # get unique track IDs from the sorted subset dataframe
    track_ids = df_subset['spotify_track_id'].unique().tolist()

    # return only the top 5 track IDs
    return track_ids[:5]


def expand_blend(selected_tracks, name, limit=50 ):
    """Create a new playlist, get new recommendations then add those tracks
    """
    try:
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

        new_tracks = get_recommendations(sp, selected_tracks, limit)
        pl = sp.user_playlist_create(user_id, name, name)
        pl_id = pl['id']
        sp.playlist_add_items(new_tracks, pl_id)
        return pl
    except Exception as error:
        logging.info(error)
        raise ValueError


def get_recommendations(sp, selected_track_ids, limit):
    """
    This function fetches and returns recommendations from an input of
    all unique track_ids.

    Parameters:
    selected_track_ids (list): a list of strings which are Spotify track ids
    limit (int): an integer of number of new tracks to be recommended (max of 100)

    Returns:
    List[str]: a list of Spotify track URIs for the recommended tracks.
    """
    try: 
        logging.info(f'Selected track IDs: {selected_track_ids}')
        results = sp.recommendations(seed_tracks=selected_track_ids, limit=limit)
        logging.info("Received recomendation results")
        recommended_track_uris = ['spotify:track:' + str(track['id']) for track in results['tracks']]
        recommended_track_uris += ['spotify:track:' + str(id) for id in selected_track_ids] # add back original
        return recommended_track_uris
    except Exception as error:
        logging.error(f'Error occurred: {error}')
        logging.error(traceback.format_exc())
        return "Please try again"


def create_event_playlist(groovy_event, link):
    try:
        # Example script to expand playlist
        playlistID = gd.get_playlist_id(link)
        df = pd.read_csv(f'{playlistID}.csv')
        selection = get_top_five_selected_tracks(df, groovy_event)
        #playlist = expand_blend(selection, selected_tracks)
        limit = 50
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

        new_tracks = get_recommendations(sp, selection, limit)
        playlist = sp.user_playlist_create(user_id, groovy_event, public=True, description=groovy_event)
        playlist_id = playlist['id']

        sp.playlist_add_items(playlist_id, new_tracks)
        return playlist
    except Exception as error:
        logging.error(f'Error occurred: {error}')
        logging.error(traceback.format_exc())
        return "Please try again"