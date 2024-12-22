app.py "from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# Function to fetch the audio URL from YouTube using yt-dlp
def get_audio_url(query):
    search_url = f"ytsearch:{query}"
    ydl_opts = {
        'format': 'bestaudio/best',  # Best audio quality
        'noplaylist': True,          # Don't fetch playlists
        'quiet': True,               # Suppress logs
        'cookiefile': 'cookies.txt', # Path to cookies.txt
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            video = info['entries'][0]  # Get the first result
            return video['url']         # Return the audio URL
    except Exception as e:
        raise RuntimeError(f"Error fetching audio: {str(e)}")

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the search request
@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is missing'}), 400

    try:
        audio_url = get_audio_url(query)
        return jsonify({'audio_url': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
