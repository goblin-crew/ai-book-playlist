from config import LOG_LEVEL, print_configuration
from langchain_utils import extract_chapter_info, generate_spotify_parameters
from spotify_utils import create_playlist_with_description, initialize_spotify, get_spotify_recommendations, create_spotify_playlist, get_available_genre_seeds
from playlist_config import save_config, load_config, select_config_file
import logging

# Set up logging
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def get_user_input():
    book_title = input("Enter the book title: ")
    user_input = input("Enter any comments about the book and summaries of some chapters: ")
    music_preferences = input("Enter any music preferences (e.g., genre, instrumental only): ")
    vocal_preference = input("Do you want vocal tracks, instrumental tracks, or both? ((v)ocal/(i)nstrumental/(b)oth): ")
    min_instrumentalness = input("Enter a minimum instrumentalness value (0-1) or press Enter to skip: ")
    return {
        "book_title": book_title,
        "user_input": user_input,
        "music_preferences": music_preferences,
        "vocal_preference": vocal_preference,
        "min_instrumentalness": min_instrumentalness
    }

def main():
    logging.info("Application started.")
    print_configuration()  # Output the configuration at startup
    
    sp = initialize_spotify()
    if not sp:
        logging.error("Failed to initialize Spotify. Exiting.")
        return

    use_existing_config = input("Do you want to use an existing configuration? (y/n): ").lower() == 'y'

    if use_existing_config:
        config_name = select_config_file()
        if config_name:
            config = load_config(config_name)
            logging.info(f"Loaded configuration: {config_name}")
        else:
            logging.info("No configuration selected. Exiting.")
            return
    else:
        config = get_user_input()

    book_title = config['book_title']
    user_input = config['user_input']
    music_preferences = config['music_preferences']
    vocal_preference = config['vocal_preference']
    min_instrumentalness = config['min_instrumentalness']
    
    if (not use_existing_config):
        do_save_config = input("Do you want to save this configuration for future use? (y/n): ").lower() == 'y'
        # Save the configuration if it's new
        if do_save_config:
            config_name = input("Enter a name for this configuration: ")
            save_config(config, config_name)

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

            # Add vocal_preference and min_instrumentalness to parameters
            parameters['vocal_preference'] = vocal_preference
            if min_instrumentalness_value is not None:
                parameters['min_instrumentalness'] = min_instrumentalness_value

            playlist_url = create_playlist_with_description(sp, book_title, chapter['number'], tracks, parameters)
            if playlist_url:
                logging.info(f"Playlist for Chapter {chapter['number']} created: {playlist_url}")
            else:
                logging.error(f"Failed to create playlist for Chapter {chapter['number']}")
        else:
            logging.error(f"Failed to generate parameters for Chapter {chapter['number']}")

if __name__ == "__main__":
    main()
