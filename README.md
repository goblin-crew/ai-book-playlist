# Spotify AI Book Playlist Generator

This tool generates Spotify playlists for each chapter of a book, using AI to extract chapter information, match the mood and theme of each chapter with appropriate songs, and create custom playlists. It leverages OpenAI's language model to interpret book information and Spotify's recommendation engine to select suitable tracks.

## How It Works

1. The user provides the book title, general comments about the book, and summaries of some chapters.
2. An AI model extracts and completes chapter information, including the number of chapters and summaries for all chapters.
3. For each chapter, the AI generates Spotify recommendation parameters based on the chapter's mood and theme.
4. These parameters are used to query Spotify's "Get Recommendations" endpoint, which returns a list of suitable tracks.
5. A new Spotify playlist is created for each chapter, populated with the recommended tracks.

## Prerequisites

- Python 3.9 or higher
- Conda (for environment management)
- OpenAI API key
- Spotify Developer account and API credentials

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/spotify-ai-playlists.git
   cd spotify-ai-playlists
   ```

2. Create and activate the Conda environment:
   ```
   conda env create -f environment.yml
   conda activate spotify-ai-playlists
   ```

3. Copy the `example.env` file to `.env` and set up your API keys:
   ```
   cp example.env .env
   ```
   Then edit the `.env` file with your actual API keys and desired configuration:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SPOTIFY_CLIENT_ID=your_spotify_client_id_here
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
   OPENAI_MODEL=text-davinci-002
   OPENAI_API_BASE=https://api.openai.com/v1
   ```

4. Check your environment setup:
   ```
   python check_environment.py
   ```
   This script will verify that your environment is correctly set up and all necessary dependencies are installed.

5. Run the main script:
   ```
   python spotify_book_playlist_generator.py
   ```

6. Follow the prompts to enter book information and generate playlists.

## Usage

The script will ask for the following information:
- Book title
- Comments about the book and summaries of some chapters
- Music preferences (e.g., genre, instrumental only)

After providing this information, the script will:
1. Use AI to extract and complete chapter information
2. Generate Spotify recommendation parameters for each chapter using AI
3. Use these parameters to get track recommendations from Spotify
4. Create a playlist for each chapter with the recommended tracks
5. Provide links to the created playlists

## Configuration

You can customize the following options in the `.env` file:

- `OPENAI_MODEL`: The OpenAI model to use (default: "text-davinci-002")
- `OPENAI_API_BASE`: The base URL for the OpenAI API (default: "https://api.openai.com/v1")

## Environment

The project uses a Conda environment specified in the `environment.yml` file. This ensures that all dependencies are correctly installed and managed. To update the environment after changes to the `environment.yml` file, run:

```
conda env update -f environment.yml
```

If you've previously installed the environment, you may need to update it to include the latest changes:

```
conda activate spotify-ai-playlists
conda env update -f environment.yml --prune
```

## Troubleshooting

If you encounter any issues:

1. Run `check_environment.py` to verify your setup.
2. Ensure your `.env` file contains the correct API keys and configuration.
3. Make sure you've activated the Conda environment: `conda activate spotify-ai-playlists`
4. If you've updated the `environment.yml` file, run: `conda env update -f environment.yml --prune`

## Files in this project

- `spotify_book_playlist_generator.py`: The main script that generates playlists.
- `check_environment.py`: A script to verify the environment setup.
- `.env`: Contains your API keys and configuration (you need to create this file from `example.env`).
- `example.env`: An example configuration file.
- `environment.yml`: Specifies the Conda environment.
- `README.md`: This file, containing setup and usage instructions.

## Note

Make sure you have the necessary permissions and comply with all relevant terms of service when using this tool. The effectiveness of the generated playlists depends on the quality of the book information provided and the availability of suitable tracks on Spotify. The AI-generated chapter information may not always be completely accurate, especially for less well-known books.
