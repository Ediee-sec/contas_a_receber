from flask import Flask, render_template, request, jsonify
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[3]))
from source.modules.backend.mola import Mola
import os
import time
from queue import Queue
from threading import Thread
import tempfile

app = Flask(__name__)
ROOT = str(Path(__file__).resolve().parents[3])

task_status = {}

def process_file(task_id, file_path, message, email, status_queue):
    try:
        task_status[task_id] = {'status': 'processing', 'progress': 0}
        
        with open(file_path, 'rb') as file:
            Mola(file=file, message=message, email=email).flow()
        
        task_status[task_id] = {'status': 'completed', 'progress': 100}
    except Exception as e:
        task_status[task_id] = {'status': 'error', 'message': str(e)}
    finally:
        try:
            os.remove(file_path)
        except:
            pass
    
    

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    email = request.form.get('email')
    message = request.form.get('message')
    
    task_id = str(time.time())
    
    temp_fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
    try:
        with os.fdopen(temp_fd, 'wb') as tmp:
            file.save(tmp)

        status_queue = Queue()
        thread = Thread(target=process_file, args=(task_id, temp_path, message, email, status_queue))
        thread.daemon = True  
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Processamento iniciado'
        }), 202
    except Exception as e:
        try:
            os.remove(temp_path)
        except:
            pass
        raise e
    
    
@app.route('/status/<task_id>')
def get_status(task_id):
    status = task_status.get(task_id, {'status': 'not_found'})
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_debugger=True, use_reloader=False)