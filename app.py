from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

def get_audio_url(query):
    search_url = f"ytsearch:{query}"
    ydl_opts = {
        'format': 'bestaudio/best[ext=m4a]/bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'age_limit': 99,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android']
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            entries = info.get('entries', [])
            for video in entries:
                if 'url' in video:
                    return video['url']
            raise RuntimeError("No valid audio found for this query.")
    except Exception as e:
        raise RuntimeError(f"Error fetching audio: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

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
