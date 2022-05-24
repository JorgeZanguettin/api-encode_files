import os
import base64
import hashlib
from flask import Flask, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask import request

UPLOAD_FOLDER = 'files'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = f'{ROOT_DIR}/files/'

if UPLOAD_FOLDER not in os.listdir(ROOT_DIR):
    os.mkdir(UPLOAD_DIR)


app = Flask(__name__)


def encode_file(path_file, filename):
    filename_ = filename.split('.')[0] # Filename without extension
    with open(f'{path_file}{filename_}.txt', 'w', encoding='utf-8') as txt_file:
        with open(f'{path_file}{filename}', 'rb') as binary_file:
            binary_file_data = binary_file.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            base64_message = base64_encoded_data.decode('utf-8')

            txt_file.write(base64_message)

    os.remove(f'{path_file}{filename}')

    return f'{path_file}{filename_}.txt'


def decode_file(hash_filename, file_extension):
    decode_path = f'{UPLOAD_DIR}{hash_filename}.{file_extension}'

    with open(f'{UPLOAD_DIR}{hash_filename}.txt', 'rb') as txt_file:
        with open(decode_path, 'wb') as file_to_save:
            decoded_image_data = base64.decodebytes(txt_file.read())
            file_to_save.write(decoded_image_data)

    return decode_path


@app.route('/download/<path:path>', methods=['GET', 'POST'])
def download(path):
    if request.method == 'GET':
        path_split = path.split('/')
        path = path_split[0]
        filename = path_split[-1]

        return send_from_directory(
            directory='files/',
            path=path,
            filename=filename
        )


@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        if request.files:
            file = request.files['file']

            filename = 'encoded_' + str(secure_filename(file.filename))
            file_extension = filename.split('.')[-1]

            hash_object = hashlib.md5(filename.encode())
            filename_md5 = hash_object.hexdigest() + '.' + file_extension

            file.save(os.path.join(UPLOAD_DIR, filename_md5))
            path = encode_file(UPLOAD_DIR, filename_md5)
            if path[0] == '/':
                path = path[1:]

            return jsonify(
                download_url='http://127.0.0.1:8500'+url_for('download', path=path),
                hash_file=filename_md5,
                file_extension=file_extension
            )
        
        return "No File"

    return "Method Not Allowed"


@app.route('/decode', methods=['POST'])
def decode():
    if request.method == 'POST':
        if 'hash_file' in request.json and 'file_extension' in request.json:
            hash_file, file_extension = request.json['hash_file'], request.json['file_extension']

            path = decode_file(hash_file, file_extension)
            if path[0] == '/':
                path = path[1:]

            return jsonify(
                download_url='http://127.0.0.1:8500'+url_for('download', path=path)
            )

        return "No File"

    return "Method Not Allowed"


@app.route('/')
def home():
    return "Endpoint actived!!"


app.run(host='0.0.0.0', port=8500, debug=True)
