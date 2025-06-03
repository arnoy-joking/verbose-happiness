from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

# Premium proxy configuration
PROXIES = {
    'http': 'http://kiiuqioq:kossz8s8m335@23.94.138.75:6349',
    'https': 'http://kiiuqioq:kossz8s8m335@64.64.118.149:6732'
}

@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    if not video_id or len(video_id) != 11:
        video_id = extract_video_id(video_id) or video_id
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            proxies=PROXIES,  # Using authenticated proxies
            languages=None   # All languages
        )
        
        return jsonify({
            "video_id": video_id,
            "transcript": transcript,
            "transcript_text": " ".join([t['text'] for t in transcript])
        })
        
    except Exception as e:
        return jsonify({
            "error": "Proxy connection failed" if "proxies" in str(e) else str(e),
            "message": "Failed to retrieve transcript"
        }), 500

def extract_video_id(url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url or "")
        if match:
            return match.group(1)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
