from flask import Flask, render_template, request, redirect, url_for
import subprocess
import re
from pathlib import Path
import os

app = Flask(__name__)

def url_validator(url):
    """
    Validate the provided YouTube URL and determine its type.

    Args:
        url (str): The YouTube URL to validate.

    Returns:
        str: The type of URL if valid ('playlist', 'video', 'shorts'), or False if invalid.
    """
    validate_url = (
        r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/|shorts\/|playlist\?list=)?)([\w\-]+)(\S+)?$'
    )
    validate_YouTube_url = re.fullmatch(validate_url, url)
    if validate_YouTube_url:
        path = validate_YouTube_url.group(4)
        if 'playlist' in path:
            return "playlist"
        elif 'shorts' in path:
            return "shorts"
        elif 'v=' in path or 'youtu.be' in url:
            return "video"
    return False

def download_video(youtube_url, format_option):
    """
    Download the YouTube video or playlist in the specified format.

    Args:
        youtube_url (str): The YouTube URL.
        format_option (str): The desired format (e.g., mp3, mp4-720p, etc.).

    Returns:
        dict: A dictionary containing 'success' and 'message'.
    """
    try:
        download_folder = str(os.path.join(Path.home(), 'Downloads'))
        command = ['yt-dlp', '-o', f'{download_folder}/%(title)s.%(ext)s']
        
        # Adjust the format based on user selection
        if format_option == 'mp3':
            command.extend(['-x', '--audio-format', 'mp3'])
        elif format_option == 'mp4-720p':
            command.extend(['-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]'])
        elif format_option == 'mp4-1080p':
            command.extend(['-f', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'])
        
        command.append(youtube_url)
        subprocess.run(command, check=True)
        return {'success': True, 'message': 'Download Successful'}
    except subprocess.CalledProcessError as e:
        return {'success': False, 'message': f'Error: {str(e)}'}

@app.route("/download", methods=['GET', 'POST'])
def download():
    message = ''
    errorType = None

    if request.method == 'POST' and 'YouTube_url' in request.form and 'Format_selector' in request.form:
        YouTube_url = request.form['YouTube_url'].strip()
        format_option = request.form['Format_selector']
        
        if YouTube_url:
            # Validate and download video
            result = download_video(YouTube_url, format_option)
            message = result['message']
            errorType = 1 if result['success'] else 0
            
            # Redirect to avoid re-triggering the download on refresh
            return redirect(url_for('download', message=message, errorType=errorType))
        else:
            message = 'Please Enter URL'
            errorType = 0

    # Render the template with optional message
    message = request.args.get('message', '')
    errorType = request.args.get('errorType', None)
    return render_template('download.html', message=message, errorType=errorType)

@app.route("/")
def home():
    return render_template('Youtube_Page.html')

if __name__ == "__main__":
    app.run()