import random
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

def reduce_seeds(parameters):
    seed_types = ['seed_genres', 'seed_tracks', 'seed_artists']
    total_seeds = sum(len(parameters.get(seed_type, [])) for seed_type in seed_types)
    
    if total_seeds <= 5:
        return parameters

    reduced_seeds = {seed_type: parameters.get(seed_type, []).copy() for seed_type in seed_types}
    while sum(len(seeds) for seeds in reduced_seeds.values()) > 5:
        # Find the seed type with the most seeds
        max_seed_type = max(reduced_seeds, key=lambda x: len(reduced_seeds[x]))
        if len(reduced_seeds[max_seed_type]) > 0:
            # Remove a random seed from the seed type with the most seeds
            reduced_seeds[max_seed_type].pop(random.randint(0, len(reduced_seeds[max_seed_type]) - 1))

    # Update the parameters with the reduced seeds
    for seed_type in seed_types:
        if reduced_seeds[seed_type]:
            parameters[seed_type] = reduced_seeds[seed_type]
        elif seed_type in parameters:
            del parameters[seed_type]

    return parameters

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
        1. 'seed_genres': A list of 1 to 5 genres that match the chapter's mood and theme, chosen precisely from the available genres.
        2. 'seed_tracks': A list of 1 to 5 track names (including artist names) that match the chapter's mood and theme. Use your knowledge to suggest appropriate tracks.
        3. 'seed_artists': A list of 1 to 5 artist names that match the chapter's mood and theme. Use your knowledge to suggest appropriate artists.
        4. 'target_valence': A float between 0 and 1 representing the musical positiveness.
        5. 'target_energy': A float between 0 and 1 representing the intensity and activity.
        6. 'target_tempo': An integer representing the estimated tempo in BPM.
        7. 'limit': An integer for the number of tracks to return (max 50).

        Important: Provide at least 1 and up to 5 items for each of seed_genres, seed_tracks, and seed_artists. The total number of seeds across all three categories should not exceed 5.

        Format the output as a valid JSON object, ensuring that the 'seed_genres', 'seed_tracks', and 'seed_artists' are properly formatted as lists.
        """
    )

    llm = initialize_openai()
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        logging.info("Generating Spotify parameters.")
        result = chain.run(book_title=book_title, chapter_summary=chapter_summary, music_preferences=music_preferences, available_genres=", ".join(available_genres), timeout=30)  # Added timeout
        logging.info("Received raw parameters response from OpenAI.")
        parameters = json.loads(clean_json_response(result))
        parameters = reduce_seeds(parameters)
        logging.info(f"Reduced parameters: {parameters}")
        

        # Validate parameters
        total_seeds = len(parameters.get('seed_genres', [])) + len(parameters.get('seed_tracks', [])) + len(parameters.get('seed_artists', []))
        if total_seeds == 0 or total_seeds > 5:
            logging.error(f"Invalid total number of seeds: {total_seeds}. Must be between 1 and 5.")
            return None

        for seed_type in ['seed_genres', 'seed_tracks', 'seed_artists']:
            if seed_type in parameters and (len(parameters[seed_type]) < 1 or len(parameters[seed_type]) > 5):
                logging.error(f"Invalid {seed_type}: Must contain between 1 and 5 items.")
                return None
        
        for feature in ['valence', 'energy']:
            target_key = f'target_{feature}'
            if not (0 <= parameters[target_key] <= 1):
                logging.error(f"Invalid {target_key}: Must be between 0 and 1.")
                return None

        if not isinstance(parameters['target_tempo'], (int, float)) or parameters['target_tempo'] < 0:
            logging.error("Invalid target_tempo: Must be a non-negative number.")
            return None

        if not isinstance(parameters['limit'], int) or parameters['limit'] <= 0 or parameters['limit'] > 50:
            logging.error("Invalid limit: Must be an integer between 1 and 50.")
            return None

        logging.info("Successfully generated Spotify parameters.")
        return parameters
    except Exception as e:
        logging.error(f"Error generating Spotify parameters: {e}")
        return None
