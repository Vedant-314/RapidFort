import os
import pythoncom
from flask import Flask, request, render_template, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from docx2pdf import convert

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static/pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_pdf(input_path, output_path):
    pythoncom.CoInitialize()
    try:
        convert(input_path, output_path)
    finally:
        pythoncom.CoUninitialize()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_size = os.path.getsize(file_path)
        metadata = {
            'filename': filename,
            'size': file_size,
            'size_human': f"{file_size / (1024 * 1024):.2f} MB"  
        }

        return jsonify({'message': 'File uploaded successfully', 'metadata': metadata, 'file_path': file_path})

    return jsonify({'error': 'Only .docx files are allowed'}), 400

@app.route('/convert', methods=['POST'])
def convert_to_pdf_route():
    file_path = request.form['file_path']
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    pdf_filename = os.path.splitext(os.path.basename(file_path))[0] + '.pdf'
    pdf_path = os.path.join(app.config['STATIC_FOLDER'], pdf_filename)

    try:
        convert_to_pdf(file_path, pdf_path)
        
        pdf_url = url_for('static', filename=f'pdfs/{pdf_filename}')
        return jsonify({'pdf_url': pdf_url})

    except Exception as e:
        return jsonify({'error': f"Error converting file: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
