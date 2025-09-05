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

    print("Received transcript:")
    print(transcript)
    current_thread = threading.Thread(target=start_execution, args=(transcript,stop_flag, log_queue))
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
    #zip the output folder and send it as a download
    zip_path = os.path.abspath("output.zip")
    output_dir = "output"
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', output_dir)
    return send_file(zip_path, as_attachment=True)

@app.route('/')
def index():
    return open("index.html", encoding="utf-8").read()

app.run(host="0.0.0.0", port=8080, debug=True)
