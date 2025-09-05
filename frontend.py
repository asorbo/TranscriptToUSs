from flask import Flask, request, jsonify, Response
from main import start_execution
import time
import threading
import queue

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
    return Response(generate(), mimetype='text/event-stream')    

@app.route('/')
def index():
    return open("index.html", encoding="utf-8").read()

app.run(host="0.0.0.0", port=8080, debug=True)
