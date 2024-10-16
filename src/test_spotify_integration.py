import logging
from spotify_utils import initialize_spotify, get_spotify_recommendations, get_available_genre_seeds
from langchain_utils import generate_spotify_parameters

logging.basicConfig(level='DEBUG', format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def test_spotify_integration():
    # Initialize Spotify client
    sp = initialize_spotify()
    if not sp:
        print("Failed to initialize Spotify client.")
        return
    

    # Get available genre seeds
    available_genres = get_available_genre_seeds(sp)
    print("Available Genre Seeds:", available_genres)

    # Sample data for testing
    book_title = "The Giver"
    chapter_summary = "Jonas's parents talk to him about the Ceremony of Twelve, reassuring him that the Elders observe children carefully and make the right assignments. Although anxious, Jonas trusts the process but is uncertain about his future role."
    music_preferences = "Instrumental. No Vocals"

    # Generate Spotify parameters
    parameters = generate_spotify_parameters(book_title, chapter_summary, music_preferences, available_genres)
    if not parameters:
        print("Failed to generate Spotify parameters.")
        return

    # Ensure the seed genres are valid
    valid_seed_genres = [genre for genre in parameters['seed_genres'] if genre in available_genres]
    if not valid_seed_genres:
        print("No valid seed genres found. Please check the generated genres.")
        return

    parameters['seed_genres'] = valid_seed_genres
    print("Generated Spotify Parameters:", parameters)

    # Get recommendations
    tracks = get_spotify_recommendations(sp, parameters)
    if tracks:
        print("Recommended Tracks:")
        for track in tracks:
            print(f"- {track['name']} by {track['artists'][0]['name']}")
    # Create a playlist with the recommended tracks
        playlist_name = f"{book_title} Playlist"
        playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, public=False)
        track_uris = [track['uri'] for track in tracks]
        sp.playlist_add_items(playlist['id'], track_uris)
        description = "Parameters used:"
        for key, value in parameters.items():
            description += f"{key}: {value}; "
        sp.playlist_change_details(playlist['id'], description=description, public=False)
        
    else:
        print("No tracks found.")

if __name__ == "__main__":
    test_spotify_integration()
