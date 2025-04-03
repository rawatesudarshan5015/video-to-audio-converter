# app_yt_dlp.py
from flask import Flask, render_template, request, send_file, url_for, redirect
import os
import uuid
import re
import subprocess
from pathlib import Path

app = Flask(__name__)

# Create directories if they don't exist
UPLOAD_FOLDER = 'static/downloads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get YouTube URL from form
            youtube_url = request.form['youtube_url']

            # Validate YouTube URL
            if not is_valid_youtube_url(youtube_url):
                return render_template('index.html', error="Invalid YouTube URL. Please enter a valid YouTube URL.")

            # Create a unique ID for this download
            download_id = str(uuid.uuid4())
            output_path = os.path.join(UPLOAD_FOLDER, f"{download_id}.mp3")

            print(f"Processing URL: {youtube_url}")

            # Use yt-dlp to download and extract audio
            command = [
                'yt-dlp',
                '-x',  # Extract audio
                '--audio-format', 'mp3',  # Convert to mp3
                '--audio-quality', '0',  # Best quality
                '-o', output_path,  # Output file
                youtube_url  # URL to process
            ]

            print(f"Running command: {' '.join(command)}")
            process = subprocess.run(command, capture_output=True, text=True)

            if process.returncode != 0:
                print(f"Error output: {process.stderr}")
                return render_template('index.html', error=f"Download failed: {process.stderr}")

            print(f"Success output: {process.stdout}")

            # Get video title from yt-dlp output
            title_match = re.search(r'\[download\] Destination: .+?/(.+?)\.', process.stdout)
            if title_match:
                video_title = title_match.group(1)
            else:
                video_title = Path(output_path).stem

            # Generate download URL
            download_url = url_for('download_file', filename=f"{Path(output_path).name}")

            return render_template('index.html',
                                   success=True,
                                   video_title=video_title,
                                   download_url=download_url)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR: {str(e)}")
            print(error_details)
            return render_template('index.html', error=f"An error occurred: {str(e)}")

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)


def is_valid_youtube_url(url):
    """Simple validation for YouTube URLs"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_match = re.match(youtube_regex, url)
    return youtube_match is not None


if __name__ == '__main__':
    app.run(debug=True)