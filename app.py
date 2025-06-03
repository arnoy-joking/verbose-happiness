from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

@app.route('/transcript', methods=['GET'])
def get_transcript():
    video_id = request.args.get('video_id')
    if not video_id or len(video_id) != 11:
        return jsonify({"error": "Invalid YouTube video ID"}), 400
    
    try:
        # Try to get transcript without specifying language
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=None  # Fetch any available language
        )
        return jsonify({
            "video_id": video_id,
            "transcript": transcript,
            "transcript_text": " ".join([t['text'] for t in transcript])
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "No transcript available for this video"
        }), 404

def extract_video_id(url):
    # Extract ID from URL if provided instead of ID
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
