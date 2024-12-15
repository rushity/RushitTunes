from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# Function to fetch the audio URL using yt-dlp with --cookies-from-browser
def get_audio_url(query):
    search_url = f"ytsearch:{query}"  # Search query on YouTube
    ydl_opts = {
        'format': 'bestaudio/best',        # Fetch the best audio format
        'noplaylist': True,               # Avoid playlists
        'quiet': True,                    # Suppress verbose output
        'cookiesfrombrowser': ('chrome',),  # Automatically fetch cookies from Chrome
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)  # Extract video/audio info
            video = info['entries'][0]  # Take the first search result
            return video['url']  # Return the audio URL
    except Exception as e:
        raise RuntimeError(f"Error fetching audio: {str(e)}")

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for searching a song
@app.route('/search', methods=['POST'])
def search():
    data = request.json  # Parse JSON data from the frontend
    query = data.get('query')  # Get the "query" parameter

    if not query:
        return jsonify({'error': 'Query parameter is missing'}), 400

    try:
        # Get the audio URL
        audio_url = get_audio_url(query)
        return jsonify({'audio_url': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
