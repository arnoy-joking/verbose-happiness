from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import socket
import urllib3

app = Flask(__name__)

# Configure verified proxy
PROXIES = {
    "http": "http://kiiuqioq:kossz8s8m335@23.94.138.75:6349",
    "https": "http://kiiuqioq:kossz8s8m335@23.94.138.75:6349"
}

def debug_proxy_connection():
    """Deep diagnostic for proxy issues"""
    tests = {
        "TCP Connection": lambda: socket.create_connection(("23.94.138.75", 6349), timeout=5),
        "HTTP Test": lambda: requests.get("http://example.com", proxies=PROXIES, timeout=5),
        "HTTPS Test": lambda: requests.get("https://example.com", proxies=PROXIES, timeout=5),
        "YouTube API Test": lambda: YouTubeTranscriptApi.get_transcript("dQw4w9WgXcQ", proxies=PROXIES)
    }
    
    results = {}
    for name, test in tests.items():
        try:
            test()
            results[name] = "✅ Success"
        except Exception as e:
            results[name] = f"❌ Failed: {type(e).__name__}: {str(e)}"
    
    return results

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    # First verify proxy connectivity
    debug_info = debug_proxy_connection()
    
    if "❌" in "\n".join(debug_info.values()):
        return jsonify({
            "status": "proxy_configuration_error",
            "debug_info": debug_info,
            "solution_steps": [
                "1. Verify credentials are correct",
                "2. Check firewall rules allow outbound connections",
                "3. Contact colocrossing.com support about port 6349",
                "4. Try proxy in different network environment"
            ]
        }), 502

    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            proxies=PROXIES,
            languages=None
        )
        return jsonify({
            "proxy_debug": debug_info,
            "transcript": transcript
        })
    except Exception as e:
        return jsonify({
            "error": type(e).__name__,
            "message": str(e),
            "proxy_troubleshooting": {
                "verify_connectivity": "curl -x http://kiiuqioq:kossz8m335@23.94.138.75:6349 https://api.ipify.org",
                "colocrossing_support": "support@colocrossing.com"
            }
        }), 503
