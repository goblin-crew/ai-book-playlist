import os
from dotenv import load_dotenv
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

# Load environment variables
load_dotenv()

# Get OpenAI configuration from environment variables
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "text-davinci-002")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# Initialize OpenAI client
llm = OpenAI(model_name=OPENAI_MODEL, openai_api_base=OPENAI_API_BASE, temperature=0.7)

# Initialize Spotify client
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri="http://localhost:8888/callback",
        scope="playlist-modify-private"
    ))
except Exception as e:
    print(f"Error initializing Spotify client: {e}")
    print("Please check your Spotify API credentials in the .env file.")
    exit(1)

def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False

def extract_chapter_info(book_title, user_input, max_retries=3, initial_tokens=1000):
    prompt = PromptTemplate(
        input_variables=["book_title", "user_input"],
        template="""
        Based on the following information about the book "{book_title}", extract and complete chapter information:

        User input: {user_input}

        Please provide the following:
        1. The total number of chapters in the book.
        2. A brief summary for each chapter (even for chapters not mentioned in the user input).

        Format the output as a JSON object with the following structure:
        {{
            "num_chapters": <integer>,
            "chapters": [
                {{"number": 1, "summary": "<chapter 1 summary>"}},
                {{"number": 2, "summary": "<chapter 2 summary>"}},
                ...
            ]
        }}
        """
    )

    for attempt in range(max_retries):
        try:
            custom_llm = OpenAI(model_name=OPENAI_MODEL, openai_api_base=OPENAI_API_BASE, temperature=0.7, max_tokens=initial_tokens * (attempt + 1))
            chain = LLMChain(llm=custom_llm, prompt=prompt)
            result = chain.run(book_title=book_title, user_input=user_input)
            
            if is_valid_json(result):
                chapter_info = json.loads(result)
                return chapter_info
            else:
                print(f"Attempt {attempt + 1}: Invalid JSON response. Retrying with increased token limit.")
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error extracting chapter information: {e}")
        
    print("Failed to extract valid chapter information after multiple attempts.")
    return None

def generate_spotify_parameters(book_title, chapter_summary, music_preferences):
    prompt = PromptTemplate(
        input_variables=["book_title", "chapter_summary", "music_preferences"],
        template="""
        Based on the following information about a book chapter, generate parameters for Spotify's recommendation API:
        Book: {book_title}
        Chapter summary: {chapter_summary}
        Music preferences: {music_preferences}

        Please provide the following parameters as a JSON object:
        1. 'seed_genres': A list of up to 5 genres that match the chapter's mood and theme.
        2. 'target_valence': A float between 0 and 1 representing the musical positiveness.
        3. 'target_energy': A float between 0 and 1 representing the intensity and activity.
        4. 'target_tempo': An integer representing the estimated tempo in BPM.
        5. 'limit': An integer for the number of tracks to return (max 100).

        Format the output as a valid JSON object.
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        result = chain.run(book_title=book_title, chapter_summary=chapter_summary, music_preferences=music_preferences)
        parameters = json.loads(result)
        return parameters
    except Exception as e:
        print(f"Error generating Spotify parameters: {e}")
        return None

def get_spotify_recommendations(parameters):
    try:
        recommendations = sp.recommendations(
            seed_genres=parameters['seed_genres'],
            target_valence=parameters['target_valence'],
            target_energy=parameters['target_energy'],
            target_tempo=parameters['target_tempo'],
            limit=parameters['limit']
        )
        return recommendations['tracks']
    except Exception as e:
        print(f"Error getting Spotify recommendations: {e}")
        return []

def create_spotify_playlist(book_title, chapter_number, tracks):
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

def main():
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
            tracks = get_spotify_recommendations(parameters)
            playlist_url = create_spotify_playlist(book_title, chapter['number'], tracks)
            if playlist_url:
                print(f"Playlist for Chapter {chapter['number']} created: {playlist_url}")
            else:
                print(f"Failed to create playlist for Chapter {chapter['number']}")
        else:
            print(f"Failed to generate parameters for Chapter {chapter['number']}")

if __name__ == "__main__":
    main()
