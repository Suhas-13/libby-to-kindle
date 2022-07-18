import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from helper import *






ALLOWED_EXTENSIONS = {'epub', 'acsm'}

app = Flask(__name__)
app.config['ACSM_FOLDER'] = ACSM_FOLDER
app.config['MOBI_FOLDER'] = MOBI_FOLDER
app.config['EPUB_FOLDER'] = EPUB_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 48 * 1000 * 1000



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def acsm_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "acsm"

def epub_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "epub"

def mobi_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "mobi"
           
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if acsm_file(file.filename):
                file.save(os.path.join(app.config['ACSM_FOLDER'], filename))
                PROCESS_LIST.enqueue(remove_drm, filename)
            elif epub_file(file.filename):
                file.save(os.path.join(app.config['EPUB_FOLDER'], filename))
                PROCESS_LIST.enqueue(convert_epub_to_mobi, filename)
            elif mobi_file(file.filename):
                file.save(os.path.join(app.config['EPUB_FOLDER'], filename))
                PROCESS_LIST.enqueue(email_kindle, filename)
            return redirect(request.url)
    return '''
    <!doctype html>
    <title>Upload Books</title>
    <h1>Upload Books</h1>
    <form method=post enctype=multipart/form-data>
      <input multiple type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
    
if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0')