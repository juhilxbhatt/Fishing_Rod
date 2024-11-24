from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/download" , methods=['GET', 'POST'])
def download():
    return render_template('download.html')

if __name__ == "__main__":
    app.run()