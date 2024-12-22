from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import time

app = Flask(__name__)

# Create a folder to store downloaded files
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Global variable to track download progress
download_progress = 0

# Function to fetch the audio URL from YouTube using yt-dlp
def get_audio_url(query):
    search_url = f"ytsearch:{query}"
    ydl_opts = {
        'format': 'bestaudio/best',  # Best audio quality
        'noplaylist': True,          # Don't fetch playlists
        'quiet': True,               # Suppress logs
        'cookiefile': 'cookies.txt', # Path to cookies.txt
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # Save to the 'downloads' folder
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            video = info['entries'][0]  # Get the first result
            return video['url'], video['title']  # Return the audio URL and the video title
    except Exception as e:
        raise RuntimeError(f"Error fetching audio: {str(e)}")

# Function to download the song and track the progress
def download_song(query):
    global download_progress
    download_progress = 0
    search_url = f"ytsearch:{query}"
    
    def progress_hook(d):
        nonlocal download_progress
        if d['status'] == 'downloading':
            download_progress = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': False,
        'progress_hooks': [progress_hook],  # Hook for progress updates
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_url])
    return download_progress

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
        audio_url, song_title = get_audio_url(query)
        return jsonify({'audio_url': audio_url, 'song_title': song_title})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to start the download process
@app.route('/start-download', methods=['POST'])
def start_download():
    global download_progress
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is missing'}), 400

    try:
        download_progress = download_song(query)
        return jsonify({'message': 'Download started', 'progress': download_progress})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to track the download progress
@app.route('/download-progress', methods=['GET'])
def download_progress_status():
    return jsonify({'progress': download_progress})

# Route to handle file download
@app.route('/download-file/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
