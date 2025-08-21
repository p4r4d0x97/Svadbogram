from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import zipfile
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4', 'mov'}
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            files.append({
                'name': filename,
                'url': url_for('static', filename=f'uploads/{filename}'),
                'type': 'video' if filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov'} else 'image',
                'upload_time': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            })
    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type. Allowed: png, jpg, jpeg, mp4, mov')
        return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    flash('File not found')
    return redirect(url_for('index'))


@app.route('/download_all')
def download_all():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if
             os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    if not files:
        flash('No files to download')
        return redirect(url_for('index'))

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            zf.write(file_path, filename)
    memory_file.seek(0)

    return send_file(
        memory_file,
        download_name='media_archive.zip',
        as_attachment=True
    )


if __name__ == '__main__':
    app.run(debug=True)
