import subprocess
from flask import Flask, request, jsonify, render_template
import os
import json
import codecs
from convert_trace import *

app = Flask(__name__)

# Uploads folder
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Get trace
@app.route('/trace', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    file = request.files['file']
    tx_hash = request.form['tx-hash']
    # if no file is selected
    if file.filename == '':
        return jsonify({'message': 'No file selected for uploading'}), 400

    # check if the file is a json file
    if not file.filename.endswith('.json'):
        return jsonify({'message': 'Uploaded file is not a json file'}), 400

    # save the file
    try:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        get_trace(file.filename, tx_hash)
        with open("result.txt", "r") as result_file:
            boogie_output = result_file.read()
        print(boogie_output)
        return jsonify({'message': 'File successfully uploaded', 'boogie-output': boogie_output}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while saving the file.'}), 500

def get_trace(theorem_fname, tx_hash):
    command = 'curl -H "Content-Type: application/json" --data "{\\"jsonrpc\\":\\"2.0\\", \\"id\\": 1, \\"method\\": \\"debug_traceTransaction\\", \\"params\\": [\\"' + tx_hash + '\\",{} ] }" http://localhost:9545 -o client_trace.json'
    print(command)
    os.system(command)
    # Get trace
    output_trace("client_trace.json", tx_hash, "deployment_info.json", theorem_fname)
    # Get boogie output
    os.system("python3 symexec.py MultiVulnToken.sol uploads/" + theorem_fname + " trace-" + tx_hash + ".txt")
    os.system("boogie trace-" + tx_hash + ".bpl > result.txt")

# Display contents of any file
@app.route('/display')
def display_file():
    filename = request.args.get('file', default="default.txt", type=str)
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        file_content = f.read()
    return render_template('display.html', file_content=file_content)

if __name__ == '__main__':
    app.run(debug=True)
