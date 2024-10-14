from config import print_configuration
from langchain_utils import extract_chapter_info, generate_spotify_parameters
from spotify_utils import initialize_spotify, get_spotify_recommendations, create_spotify_playlist

def main():
    print_configuration()  # Output the configuration at startup
    
    sp = initialize_spotify()
    if not sp:
        print("Failed to initialize Spotify. Exiting.")
        return

    book_title = input("Enter the book title: ")
    user_input = input("Enter any comments about the book and summaries of some chapters: ")
    music_preferences = input("Enter any music preferences (e.g., genre, instrumental only): ")

    chapter_info = extract_chapter_info(book_title, user_input)
    
    if not chapter_info:
        print("Failed to extract chapter information. Exiting.")
        return

    for chapter in chapter_info['chapters']:
        parameters = generate_spotify_parameters(book_title, chapter['summary'], music_preferences)
        
        if parameters:
            tracks = get_spotify_recommendations(sp, parameters)
            playlist_url = create_spotify_playlist(sp, book_title, chapter['number'], tracks)
            if playlist_url:
                print(f"Playlist for Chapter {chapter['number']} created: {playlist_url}")
            else:
                print(f"Failed to create playlist for Chapter {chapter['number']}")
        else:
            print(f"Failed to generate parameters for Chapter {chapter['number']}")

if __name__ == "__main__":
    main()
