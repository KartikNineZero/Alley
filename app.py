import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('md.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        if not os.path.exists("D:/md prototype/dld"):
            os.makedirs("D:/md prototype/dld")
        download_path = os.path.join("D:/md prototype/dld", "downloaded_file.avif")
        with open(download_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return "Download complete!"
    except requests.exceptions.RequestException as e:
        return "Download failed: {}".format(e)

if __name__ == '__main__':
    app.run(debug=True)
