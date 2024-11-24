from flask import Flask, render_template, request
import subprocess
from pathlib import Path
import os

app = Flask(__name__)

# Function to handle video downloading
def download_video(youtube_url):
    try:
        download_folder = str(os.path.join(Path.home(), 'Downloads'))
        command = [
            'yt-dlp',
            '-o', f'{download_folder}/%(title)s.%(ext)s',  # Output format
            youtube_url
        ]
        subprocess.run(command, check=True)
        return {'success': True, 'message': 'Download Successful'}
    except subprocess.CalledProcessError as e:
        return {'success': False, 'message': f'Error: {str(e)}'}

@app.route("/download", methods=['GET', 'POST'])
def download():
    message = ''
    errorType = None
    if request.method == 'POST' and 'YouTube_url' in request.form:
        YouTube_url = request.form['YouTube_url'].strip()  # Remove any leading/trailing spaces
        print('URL Received: ' + YouTube_url)

        if YouTube_url:
            result = download_video(YouTube_url)  # Call the separate download function
            message = result['message']
            errorType = 1 if result['success'] else 0
        else:
            message = 'Please Enter URL'
            errorType = 0

    return render_template('download.html', message=message, errorType=errorType)

if __name__ == "__main__":
    app.run()