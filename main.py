from flask import Flask, request, jsonify
import requests
import re
import json
from xml.etree import ElementTree as ET

app = Flask(__name__)

@app.route("/transcript")
def get_transcript():
    video_id = request.args.get("id")
    if not video_id:
        return jsonify({"error": "No video ID provided"}), 400

    try:
        # 1. Load the video page HTML
        yt_url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        res = requests.get(yt_url, headers=headers)
        if res.status_code != 200:
            return jsonify({"error": "YouTube video fetch failed"}), 500

        html = res.text

        # 2. Extract ytInitialPlayerResponse
        match = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.*?\});", html)
        if not match:
            return jsonify({"error": "Failed to parse YouTube player response"}), 500

        player_response = json.loads(match.group(1))

        # 3. Extract caption tracks
        caption_tracks = player_response.get("captions", {}) \
            .get("playerCaptionsTracklistRenderer", {}) \
            .get("captionTracks", [])

        if not caption_tracks:
            return jsonify({"error": "No captions found for this video"}), 404

        # 4. Find English captions (auto or manual)
        caption_url = None
        for track in caption_tracks:
            if "en" in track.get("languageCode", ""):
                caption_url = track.get("baseUrl")
                break

        if not caption_url:
            return jsonify({"error": "English captions not found"}), 404

        # 5. Fetch captions (XML format)
        captions_res = requests.get(caption_url)
        root = ET.fromstring(captions_res.text)
        transcript_lines = [elem.text.replace("\n", " ") if elem.text else "" for elem in root.findall(".//text")]

        transcript = "\n".join(transcript_lines)
        return jsonify({"transcript": transcript})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"message": "YouTube Pirate Transcript API is up! 🏴‍☠️"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
