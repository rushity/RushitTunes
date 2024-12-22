from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# Function to fetch multiple audio URLs from YouTube using yt-dlp
def get_audio_urls(query):
    search_url = f"ytsearch:{query}"  # Search YouTube for the query
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Best available audio
        'noplaylist': True,                            # Don't fetch playlists
        'quiet': True,                                 # Suppress logs
        'cookiefile': 'cookies.txt',                   # Path to cookies.txt
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Convert to MP3 if necessary
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            audio_urls = [entry['url'] for entry in info.get('entries', [])]
            return audio_urls
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
        audio_urls = get_audio_urls(query)
        if not audio_urls:
            return jsonify({'error': 'No results found'}), 404
        return jsonify({'audio_urls': audio_urls})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
