from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# Function to fetch the audio URL from YouTube using yt-dlp and cookies
def get_audio_url(query):
    search_url = f"ytsearch:{query}"
    ydl_opts = {
        'format': 'bestaudio/best',  # Best audio quality
        'noplaylist': True,          # Don't fetch playlists
        'quiet': True,               # Suppress logs and output
        'cookiefile': 'cookies.txt', # Path to the exported cookies.txt file
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            video = info['entries'][0]  # Get the first search result
            return video['url']         # Return the audio URL
    except Exception as e:
        raise RuntimeError(f"Error fetching audio: {str(e)}")

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')  # Renders the main HTML page

# Route to handle the search request
@app.route('/search', methods=['POST'])
def search():
    data = request.json  # Get the data sent as JSON
    query = data.get('query')  # Safely access the 'query' parameter
    if not query:
        return jsonify({'error': 'Query parameter is missing'}), 400  # Error if query is missing

    try:
        # Fetch the audio URL for the given search query
        audio_url = get_audio_url(query)
        return jsonify({'audio_url': audio_url})  # Return the audio URL as JSON response
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return error message if an exception occurs

if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask app in debug mode
