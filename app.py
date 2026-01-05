from flask import Flask, Response, request, jsonify
import queue
import threading
import time

app = Flask(__name__)

# ================== MJPEG ==================
frame_queue = queue.Queue(maxsize=10)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        frame_queue.put_nowait(request.data)
    except queue.Full:
        pass
    return "OK"

def generate():
    while True:
        frame = frame_queue.get()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame +
            b"\r\n"
        )

@app.route("/video")
def video():
    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# ================== SETTINGS ==================
# القيم الافتراضية
settings = {
    "notifications": True,
    "objects": {
        "Person": True,
        "Car": False,
        "Animal": False,
        "Drone": False,
        "Bag": False,
        "Weapon": False,
        "Fire": False
    },
    "updated_at": time.time()
}

@app.route("/api/settings", methods=["POST"])
def update_settings():
    global settings
    data = request.json

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    settings["notifications"] = data.get("notifications", True)
    settings["objects"] = data.get("objects", settings["objects"])
    settings["updated_at"] = time.time()

    print("📩 New Settings Received:", settings)
    return jsonify({"status": "ok"})

@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify(settings)

# ================== MAIN ==================
@app.route("/")
def index():
    return "✅ MJPEG Render Server Running"
