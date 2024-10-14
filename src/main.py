from config import print_configuration
from langchain_utils import extract_chapter_info, generate_spotify_parameters
from spotify_utils import initialize_spotify, get_spotify_recommendations, create_spotify_playlist, get_available_genre_seeds
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def main():
    logging.info("Application started.")
    print_configuration()  # Output the configuration at startup
    
    sp = initialize_spotify()
    if not sp:
        logging.error("Failed to initialize Spotify. Exiting.")
        return

    book_title = input("Enter the book title: ")
    user_input = input("Enter any comments about the book and summaries of some chapters: ")
    music_preferences = input("Enter any music preferences (e.g., genre, instrumental only): ")
    vocal_preference = input("Do you want vocal tracks, instrumental tracks, or both? ((v)ocal/(i)nstrumental/(b)oth): ")
    min_instrumentalness = input("Enter a minimum instrumentalness value (0-1) or press Enter to skip: ")

    chapter_info = extract_chapter_info(book_title, user_input)
    
    if not chapter_info:
        logging.error("Failed to extract chapter information. Exiting.")
        return

    # Get available genres
    available_genres = get_available_genre_seeds(sp)

    for chapter in chapter_info['chapters']:
        logging.info(f"Processing chapter {chapter['number']}.")
        parameters = generate_spotify_parameters(book_title, chapter['summary'], music_preferences, available_genres)
        
        if parameters:
            # Convert min_instrumentalness to float if provided
            min_instrumentalness_value = float(min_instrumentalness) if min_instrumentalness else None
            tracks = get_spotify_recommendations(sp, parameters, vocal_preference, min_instrumentalness_value)
            
            # Log the number of tracks collected and some sample tracks
            if tracks:
                logging.info(f"Collected {len(tracks)} tracks for Chapter {chapter['number']}.")
                sample_tracks = [track['name'] for track in tracks[:5]]  # Get sample of first 5 track names
                logging.info(f"Sample tracks: {', '.join(sample_tracks)}")
            else:
                logging.warning(f"No tracks found for Chapter {chapter['number']}.")

            playlist_url = create_spotify_playlist(sp, book_title, chapter['number'], tracks)
            if playlist_url:
                logging.info(f"Playlist for Chapter {chapter['number']} created: {playlist_url}")
            else:
                logging.error(f"Failed to create playlist for Chapter {chapter['number']}")
        else:
            logging.error(f"Failed to generate parameters for Chapter {chapter['number']}")

if __name__ == "__main__":
    main()
