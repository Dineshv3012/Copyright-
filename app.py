from flask import Flask, request, jsonify
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# Helper to extract video ID from full URL or ID
def extract_video_id(input_str):
    if "youtube.com" in input_str or "youtu.be" in input_str:
        parsed_url = urlparse(input_str)
        if "youtu.be" in input_str:
            return parsed_url.path[1:]
        query = parse_qs(parsed_url.query)
        return query.get("v", [None])[0]
    return input_str

# Check if video is licensed using YouTube Data API
def check_video_licensed(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(
        part="contentDetails",
        id=video_id
    )
    response = request.execute()

    if not response['items']:
        return None

    content_details = response['items'][0]['contentDetails']
    return content_details.get('licensedContent', False)

@app.route('/')
def home():
    return "📺 YouTube Copyright Checker API"

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    youtube_url = data.get("youtube_url")
    api_key = os.getenv("YOUTUBE_API_KEY")

    if not youtube_url:
        return jsonify({"error": "youtube_url is required"}), 400
    if not api_key:
        return jsonify({"error": "YOUTUBE_API_KEY not set in environment"}), 500

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        is_licensed = check_video_licensed(video_id, api_key)
        if is_licensed is None:
            return jsonify({"error": "Video not found"}), 404
        return jsonify({
            "video_id": video_id,
            "copyright": bool(is_licensed),
            "licensed": bool(is_licensed)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()