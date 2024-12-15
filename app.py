from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

def get_audio_url(query):
    search_url = f"ytsearch:{query}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)
        video = info['entries'][0]  # Take the first search result
        return video['url']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json  # Use request.json to parse JSON data
    query = data.get('query')  # Safely access the query key
    if not query:
        return jsonify({'error': 'Query parameter is missing'}), 400

    try:
        audio_url = get_audio_url(query)
        return jsonify({'audio_url': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
