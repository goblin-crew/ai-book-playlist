# Spotify Book Playlist Generator

This application generates Spotify playlists based on book chapters, creating a unique musical experience that complements your reading.

## Project Structure

```
spotify-ai-playlists/
│
├── src/
│   ├── config.py
│   ├── main.py
│   ├── langchain_utils.py
│   └── spotify_utils.py
│
├── utils/
│   └── check_environment.py
│
├── .env
├── example.env
├── environment.yml
└── README.md
```

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/spotify-ai-playlists.git
   cd spotify-ai-playlists
   ```

2. Set up a conda environment using the environment.yml file:
   ```
   conda env create -f environment.yml
   conda activate spotify-ai-playlists
   ```

3. Copy the `example.env` file to `.env` and fill in your API keys:
   ```
   cp example.env .env
   ```
   Then edit the `.env` file with your OpenAI and Spotify API credentials.

4. Run the environment check:
   ```
   python utils/check_environment.py
   ```

## Usage

To run the application, use the following command:

```
python src/main.py
```

Follow the prompts to enter the book title, any comments about the book, chapter summaries, and music preferences.

The application will then:
1. Extract chapter information from your input
2. Generate Spotify parameters for each chapter
3. Create a playlist for each chapter based on the generated parameters
4. Provide you with links to the created playlists

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
