import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

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

def get_available_genre_seeds(sp):
    try:
        genres = sp.recommendation_genre_seeds()
        return genres['genres']
    except Exception as e:
        print(f"Error getting available genre seeds: {e}")
        return []

def get_spotify_recommendations(sp, parameters):
    try:
        # Validate parameters
        if not isinstance(parameters['seed_genres'], list) or len(parameters['seed_genres']) > 5:
            print("Invalid seed_genres: Must be a list of up to 5 genres.")
            return []
        if not (0 <= parameters['target_valence'] <= 1):
            print("Invalid target_valence: Must be between 0 and 1.")
            return []
        if not (0 <= parameters['target_energy'] <= 1):
            print("Invalid target_energy: Must be between 0 and 1.")
            return []
        if not isinstance(parameters['target_tempo'], int) or parameters['target_tempo'] < 0:
            print("Invalid target_tempo: Must be a non-negative integer.")
            return []
        if not (0 <= parameters.get('target_acousticness', 0) <= 1):
            print("Invalid target_acousticness: Must be between 0 and 1.")
            return []
        if not (0 <= parameters.get('target_danceability', 0) <= 1):
            print("Invalid target_danceability: Must be between 0 and 1.")
            return []
        if not (0 <= parameters.get('target_instrumentalness', 0) <= 1):
            print("Invalid target_instrumentalness: Must be between 0 and 1.")
            return []
        if not (0 <= parameters.get('target_speechiness', 0) <= 1):
            print("Invalid target_speechiness: Must be between 0 and 1.")
            return []
        if not isinstance(parameters['limit'], int) or parameters['limit'] <= 0 or parameters['limit'] > 100:
            print("Invalid limit: Must be an integer between 1 and 100.")
            return []

        recommendations = sp.recommendations(
            seed_genres=parameters['seed_genres'],
            target_valence=parameters['target_valence'],
            target_energy=parameters['target_energy'],
            target_tempo=parameters['target_tempo'],
            target_acousticness=parameters.get('target_acousticness'),
            target_danceability=parameters.get('target_danceability'),
            target_instrumentalness=parameters.get('target_instrumentalness'),
            target_speechiness=parameters.get('target_speechiness'),
            limit=parameters['limit']
        )
        return recommendations['tracks']
    except Exception as e:
        print(f"Error getting Spotify recommendations: {e}")
        return []

def create_spotify_playlist(sp, book_title, chapter_number, tracks):
    if not tracks:
        print(f"No tracks found for Chapter {chapter_number}. Skipping playlist creation.")
        return None

    try:
        playlist_name = f"{book_title} - Chapter {chapter_number} Playlist"
        playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, public=False)
        track_uris = [track['uri'] for track in tracks]
        sp.playlist_add_items(playlist['id'], track_uris)
        return playlist['external_urls']['spotify']
    except Exception as e:
        print(f"Error creating Spotify playlist: {e}")
        return None
