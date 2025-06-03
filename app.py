from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langdetect import detect
import re
import time

app = Flask(__name__)
CORS(app)

@app.route('/transcript', methods=['GET'])
def get_transcript():
    url = request.args.get('url')
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    transcript = None

    for attempt in range(4):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            break
        except TranscriptsDisabled:
            return jsonify({"error": "Transcripts are disabled for this video."}), 403
        except:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['bn'])
                break
            except:
                time.sleep(1)
                continue

    if not transcript:
        return jsonify({"error": "Transcript not found after 4 attempts"}), 500

    try:
        sample_text = " ".join([entry['text'] for entry in transcript[:5]])
        lang = detect(sample_text)
    except:
        lang = "unknown"

    formatted = format_transcript(transcript)

    return jsonify({
        "transcript": formatted,
        "language": lang
    })

def extract_video_id(url):
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

def format_transcript(transcript):
    return "\n".join(
        f"[{entry['start']:.2f}s] {entry['text']}"
        for entry in transcript
    )

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)