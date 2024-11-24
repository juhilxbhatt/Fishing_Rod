from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/download", methods=['GET', 'POST'])
def download():
    message = ''
    errorType = None
    if request.method == 'POST' and 'YouTube_url' in request.form:
        YouTube_url = request.form['YouTube_url'].strip()  # Remove any leading/trailing spaces
        print('URL Received: ' + YouTube_url)
        if YouTube_url:
            # Updated regex to handle YouTube video and playlist URLs with extra parameters
            validate_url = (
                r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$'
            )
            # Use re.fullmatch to match the entire URL
            validate_YouTube_url = re.fullmatch(validate_url, YouTube_url)
            if validate_YouTube_url:
                message = 'Starting Download'
                errorType = 1
            else:
                print("Debug: URL did not match regex.")  # Debugging statement
                message = 'Invalid URL'
                errorType = 0
        else:
            message = 'Please Enter URL'
            errorType = 0
    return render_template('download.html', message=message, errorType=errorType)

if __name__ == "__main__":
    app.run()