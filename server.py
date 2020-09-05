import os
import re
import atexit
from flask import Flask, request, redirect, render_template, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.utils import secure_filename
from server_utils.file_helper import init_folders, is_valid_file, get_path, upload_file, proccess_file, download_file, delete_old_files

app = Flask(__name__,
    template_folder='build',
    static_folder='build/static',
    static_url_path='/build/static'
)
app.config.from_pyfile('server_config.py')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        
        file = request.files["file"]
        filename = file.filename

        if filename == "":
            return redirect(request.url)
        
        if file and is_valid_file(filename):
            filename = secure_filename(filename)
            upload_file(file, filename, get_path)
            proccess_file(filename, get_path)
            return download_file(filename)

    return render_template('index.html')

# Build files from React
@app.route("/static/js/<path:path>")
def send_static_js(path):
    return send_from_directory('build/static/js', path)

@app.route("/static/css/<path:path>")
def send_static_css(path):
    return send_from_directory('build/static/css', path)

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory('build', path)

# Main
if __name__ == "__main__":
    init_folders()
    app.run()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=delete_old_files, args=(300), trigger="interval", seconds=300, max_instances=1)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())