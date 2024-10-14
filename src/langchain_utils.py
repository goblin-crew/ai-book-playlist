from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import logging
from config import OPENAI_MODEL, OPENAI_API_BASE

# Set up logging
logging.basicConfig(level=logging.INFO)

def initialize_openai():
    return ChatOpenAI(model_name=OPENAI_MODEL, openai_api_base=OPENAI_API_BASE, temperature=0.7)

def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False

def clean_json_response(response):
    # Remove any markdown formatting
    cleaned_response = response.replace("```json", "").replace("```", "").strip()
    return cleaned_response

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
            logging.info(f"Attempt {attempt + 1} to extract chapter information.")
            custom_llm = ChatOpenAI(model_name=OPENAI_MODEL, openai_api_base=OPENAI_API_BASE, temperature=0.7, max_tokens=initial_tokens * (attempt + 1))
            chain = LLMChain(llm=custom_llm, prompt=prompt)
            result = chain.run(book_title=book_title, user_input=user_input, timeout=30)  # Added timeout
            
            logging.info("Received raw response from OpenAI.")
            cleaned_result = clean_json_response(result)
            logging.info("Cleaned the response.")
            
            if is_valid_json(cleaned_result):
                chapter_info = json.loads(cleaned_result)
                logging.info("Successfully extracted chapter information.")
                return chapter_info
            else:
                logging.warning(f"Attempt {attempt + 1}: Invalid JSON response. Retrying with increased token limit.")
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}: Error extracting chapter information: {e}")
        
    logging.error("Failed to extract valid chapter information after multiple attempts.")
    return None

def generate_spotify_parameters(book_title, chapter_summary, music_preferences, available_genres):
    prompt = PromptTemplate(
        input_variables=["book_title", "chapter_summary", "music_preferences", "available_genres"],
        template="""
        Based on the following information about a book chapter, generate parameters for Spotify's recommendation API:
        Book: {book_title}
        Chapter summary: {chapter_summary}
        Music preferences: {music_preferences}
        Available genres: {available_genres}

        Please provide the following parameters as a JSON object:
        1. 'seed_genres': A list minimum 1 and maximum 5 that match the chapter's mood and theme, choose precisely,less is more, selected from the available genres, separated by commas.
        2. 'target_valence': A float between 0 and 1 representing the musical positiveness.
        3. 'target_energy': A float between 0 and 1 representing the intensity and activity.
        4. 'target_tempo': An integer representing the estimated tempo in BPM.
        5. 'target_acousticness': A float between 0 and 1 representing the acousticness of the track.
        6. 'target_danceability': A float between 0 and 1 representing how suitable a track is for dancing.
        7. 'target_instrumentalness': A float between 0 and 1 representing the likelihood that a track is instrumental.
        8. 'target_speechiness': A float between 0 and 1 representing the presence of spoken words in a track.
        9. 'limit': An integer for the number of tracks to return (max 50).

        Format the output as a valid JSON object, ensuring that the 'seed_genres' are properly formatted as a list with items separated by commas.
        """
    )

    llm = initialize_openai()
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        logging.info("Generating Spotify parameters.")
        result = chain.run(book_title=book_title, chapter_summary=chapter_summary, music_preferences=music_preferences, available_genres=", ".join(available_genres), timeout=30)  # Added timeout
        logging.info("Received raw parameters response from OpenAI.")
        parameters = json.loads(clean_json_response(result))

        # Validate parameters
        if not isinstance(parameters['seed_genres'], list) or len(parameters['seed_genres']) > 5:
            logging.error("Invalid seed_genres: Must be a list of up to 5 genres.")
            return None
        if not (0 <= parameters['target_valence'] <= 1):
            logging.error("Invalid target_valence: Must be between 0 and 1.")
            return None
        if not (0 <= parameters['target_energy'] <= 1):
            logging.error("Invalid target_energy: Must be between 0 and 1.")
            return None
        if not isinstance(parameters['target_tempo'], int) or parameters['target_tempo'] < 0:
            logging.error("Invalid target_tempo: Must be a non-negative integer.")
            return None
        if not (0 <= parameters.get('target_acousticness', 0) <= 1):
            logging.error("Invalid target_acousticness: Must be between 0 and 1.")
            return None
        if not (0 <= parameters.get('target_danceability', 0) <= 1):
            logging.error("Invalid target_danceability: Must be between 0 and 1.")
            return None
        if not (0 <= parameters.get('target_instrumentalness', 0) <= 1):
            logging.error("Invalid target_instrumentalness: Must be between 0 and 1.")
            return None
        if not (0 <= parameters.get('target_speechiness', 0) <= 1):
            logging.error("Invalid target_speechiness: Must be between 0 and 1.")
            return None
        if not isinstance(parameters['limit'], int) or parameters['limit'] <= 0 or parameters['limit'] > 50:
            logging.error("Invalid limit: Must be an integer between 1 and 100.")
            return None

        logging.info("Successfully generated Spotify parameters.")
        return parameters
    except Exception as e:
        logging.error(f"Error generating Spotify parameters: {e}")
        return None
