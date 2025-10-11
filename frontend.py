from flask import Flask, request, jsonify, Response, send_file
from main import start_execution
import time
import threading
import queue
import shutil
import os


app = Flask(__name__)

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.get_json()
    transcript = data.get('transcript', '')
    global current_thread
    current_thread = None
    global stop_flag
    stop_flag = threading.Event()
    global log_queue
    log_queue = queue.Queue()
    api_key = os.environ.get("API_KEY")
    runs_per_minute = int(os.environ.get("RUNS_PER_MINUTE", 15))

    print("Received transcript:")
    current_thread = threading.Thread(target=start_execution, args=(transcript,stop_flag, log_queue, api_key, runs_per_minute))
    current_thread.start()
    return jsonify({"message": "Transcript received successfully! Starting processing."}), 200

@app.route('/stop_execution', methods=['POST'])
def stop_execution():
    global stop_flag
    stop_flag.set()  # signal the thread to stop
    return jsonify({"message": "Stop requested"})

@app.route('/stream_logs')
def stream_logs():
    #catch any exception by rerouting to /
    global log_queue
    def generate():
        yield f"Log stream started\n\n"
        last_seen = 0
        while True:
            try:
                msg = log_queue.get(timeout=0.1)
                yield f"data: {msg}\n\n"
            except queue.Empty:
                continue
            #catch NameError: name 'log_queue' is not defined
            except Exception as e:
                #stop the stream
                yield f"event: error\ndata: {str(e)}\n\n" 
    return Response(generate(), mimetype='text/event-stream')  

@app.route('/download_outputs')
def download_outputs():
    folder_to_zip = "output_visualizer"
    zip_path = "output.zip"

    # Ensure folder exists
    os.makedirs(folder_to_zip, exist_ok=True)

    # shutil.make_archive zips the contents of a folder when you set root_dir properly
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', root_dir=folder_to_zip)

    return send_file(zip_path, as_attachment=True)

@app.route('/')
def index():
    return open("index.html", encoding="utf-8").read()

