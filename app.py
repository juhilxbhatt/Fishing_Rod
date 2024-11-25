from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import re
from pathlib import Path
import os
from flask_sse import sse

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"  # SSE requires Redis
app.register_blueprint(sse, url_prefix='/stream')

# Utility: Validate YouTube URL
def url_validator(url):
    validate_url = (
        r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/|shorts\/|playlist\?list=)?)([\w\-]+)(\S+)?$'
    )
    validate_Download_url = re.fullmatch(validate_url, url)
    if validate_Download_url:
        path = validate_Download_url.group(4)
        if 'playlist' in path:
            return "playlist"
        elif 'shorts' in path:
            return "shorts"
        elif 'v=' in path or 'youtu.be' in url:
            return "video"
    return False

# Utility: Download video with progress
def download_video_with_progress(Download_url, format_option):
    # Set the default download directory
    download_path = os.path.join(Path.home(), 'Downloads')  # Default Downloads folder

    # Command for yt-dlp
    command = ['yt-dlp', '--newline', '-o', f'{download_path}/%(title)s.%(ext)s']

    if format_option == 'mp3':
        command.extend(['-x', '--audio-format', 'mp3'])
    elif format_option == 'mp4-720p':
        command.extend(['-f', 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]'])
    elif format_option == 'mp4-1080p':
        command.extend(['-f', 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]'])

    command.append(Download_url)

    # Execute command and stream progress
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in iter(process.stdout.readline, ""):
        # Send progress to the frontend
        sse.publish({"progress": line.strip()}, type='progress')

    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        return {'success': False, 'message': 'Download failed'}
    return {'success': True, 'message': 'Download successful'}

# Route: Download logic
@app.route("/download", methods=['POST'])
def download():
    if request.method == 'POST' and 'Download_url' in request.form and 'Format_selector' in request.form:
        Download_url = request.form['Download_url'].strip()
        format_option = request.form['Format_selector']

        if Download_url:
            result = download_video_with_progress(Download_url, format_option)
            message = result['message']
            errorType = 1 if result['success'] else 0
        else:
            message = 'Please Enter URL'
            errorType = 0

        # Redirect to the homepage with status
        return redirect(url_for('render_home', message=message, errorType=errorType))
    return redirect(url_for('render_home', message='Invalid Request', errorType=0))

# Route: Render the homepage
@app.route("/", methods=['GET'])
def render_home():
    message = request.args.get('message', '')
    errorType = request.args.get('errorType', None)
    return render_template('Index.html', message=message, errorType=errorType)

if __name__ == "__main__":
    app.run()