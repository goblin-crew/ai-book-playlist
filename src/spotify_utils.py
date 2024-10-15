import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

def spotify_retry_decorator():
    def custom_wait(retry_state):
        exception = retry_state.outcome.exception()
        if isinstance(exception, spotipy.exceptions.SpotifyException) and exception.http_status == 429:
            retry_after = exception.headers.get('Retry-After', '1')
            wait_time = int(retry_after)
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying.")
            return wait_fixed(wait_time)
        logging.error(f"Error: {exception}")
        return wait_fixed(1)  # Default wait time

    return retry(
        retry=retry_if_exception_type((spotipy.exceptions.SpotifyException, ConnectionError)),
        stop=stop_after_attempt(5),
        wait=custom_wait,
        reraise=True
    )

@spotify_retry_decorator()
def initialize_spotify():
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://localhost:8888/callback",
            scope="playlist-modify-private"
        ))        
        return sp
    except Exception as e:
        print(f"Error initializing Spotify client: {e}")
        print("Please check your Spotify API credentials in the config.")
        return None
    
def print_parameters(parameters):
    print("Spotify Parameters:")
    for key, value in parameters.items():
        print(f"{key}: {value}")
        
@spotify_retry_decorator()
def get_available_genre_seeds(sp: spotipy.Spotify):
    try:
        logging.info("Getting available genre seeds...")
        genres = sp.recommendation_genre_seeds()
        return genres['genres']
    except Exception as e:
        print(f"Error getting available genre seeds: {e}")
        return []

@spotify_retry_decorator()
def search_track(sp: spotipy.Spotify, track_name):
    try:
        results = sp.search(q=track_name, type='track', limit=1)
        if results['tracks']['items']:
            return results['tracks']['items'][0]['id']
        else:
            print(f"No track found for: {track_name}")
            return None
    except Exception as e:
        print(f"Error searching for track: {e}")
        return None

@spotify_retry_decorator()
def search_artist(sp: spotipy.Spotify, artist_name):
    try:
        results = sp.search(q=artist_name, type='artist', limit=1)
        if results['artists']['items']:
            return results['artists']['items'][0]['id']
        else:
            print(f"No artist found for: {artist_name}")
            return None
    except Exception as e:
        print(f"Error searching for artist: {e}")
        return None

@spotify_retry_decorator()
def get_spotify_recommendations(sp: spotipy.Spotify, parameters, vocal_preference='b', min_instrumentalness=None):
    try:
        # Resolve track and artist names to IDs
        if 'seed_tracks' in parameters:
            seed_track_ids = [search_track(sp, track) for track in parameters['seed_tracks']]
            parameters['seed_tracks'] = [id for id in seed_track_ids if id is not None]

        if 'seed_artists' in parameters:
            seed_artist_ids = [search_artist(sp, artist) for artist in parameters['seed_artists']]
            parameters['seed_artists'] = [id for id in seed_artist_ids if id is not None]

        for feature in ['valence', 'energy']:
            target_key = f'target_{feature}'
            if target_key not in parameters or not (0 <= parameters[target_key] <= 1):
                print(f"Invalid {target_key}: Must be between 0 and 1.")
                return []

        if 'target_tempo' not in parameters or not isinstance(parameters['target_tempo'], (int, float)) or parameters['target_tempo'] < 0:
            print("Invalid target_tempo: Must be a non-negative number.")
            return []

        if not isinstance(parameters['limit'], int) or parameters['limit'] <= 0 or parameters['limit'] > 50:
            print("Invalid limit: Must be an integer between 1 and 50.")
            return []

        # Set instrumentalness based on vocal preference
        if vocal_preference == 'i':
            parameters['min_instrumentalness'] = 0.5
        elif vocal_preference == 'v':
            parameters['min_instrumentalness'] = 0
        elif vocal_preference != 'b':
            print("Invalid vocal preference: Must be '(v)ocal', '(i)nstrumental', or '(b)oth'.")
            return []

        # Set min_instrumentalness if provided
        if min_instrumentalness is not None:
            if not (0 <= min_instrumentalness <= 1):
                print("Invalid min_instrumentalness: Must be between 0 and 1.")
                return []
            parameters['min_instrumentalness'] = min_instrumentalness

        print_parameters(parameters)
        logging.info("Getting Spotify recommendations...")
        recommendations = sp.recommendations(
            seed_genres=parameters.get('seed_genres', None),
            seed_tracks=parameters.get('seed_tracks', None),
            seed_artists=parameters.get('seed_artists', None),
            target_valence=parameters['target_valence'],
            target_energy=parameters['target_energy'],
            target_tempo=parameters['target_tempo'],
            min_instrumentalness=parameters.get('min_instrumentalness'),
            limit=parameters['limit']
        )
        return recommendations['tracks']
    except Exception as e:
        print(f"Error getting Spotify recommendations: {e}")
        return []

@spotify_retry_decorator()
def create_spotify_playlist(sp: spotipy.Spotify, book_title, chapter_number, tracks):
    if not tracks:
        print(f"No tracks found for Chapter {chapter_number}. Skipping playlist creation.")
        return None

    try:
        playlist_name = f"{book_title} - Chapter {chapter_number}"
        
        # Create playlist without description
        playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, public=False)
        track_uris = [track['uri'] for track in tracks]
        sp.playlist_add_items(playlist['id'], track_uris)
        return playlist['id'], playlist['external_urls']['spotify']
    except Exception as e:
        print(f"Error creating Spotify playlist: {e}")
        return None, None

@spotify_retry_decorator()
def update_playlist_description(sp: spotipy.Spotify, playlist_id, parameters):
    try:
        # Format parameters for description
        description = "Parameters used:\n"
        for key, value in parameters.items():
            description += f"{key}: {value}\n"
        
        sp.playlist_change_details(playlist_id, description=description)
        print(f"Updated description for playlist {playlist_id}")
    except Exception as e:
        print(f"Error updating playlist description: {e}")

def create_playlist_with_description(sp: spotipy.Spotify, book_title, chapter_number, tracks, parameters):
    playlist_id, playlist_url = create_spotify_playlist(sp, book_title, chapter_number, tracks)
    if playlist_id:
        update_playlist_description(sp, playlist_id, parameters)
    return playlist_url
