from flask import Flask, jsonify, session, Response
from flask_cors import CORS
from capture import Capture

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
app.secret_key = "supersecretkey"
app.config["SESSION_COOKIE_NAME"] = "session"
app.config["SESSION_COOKIE_DOMAIN"] = "localhost"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_PERMANENT"] = False

capture = Capture()


@app.route("/sse")
def get_img_sse():
    # SSE - Server Sent Events
    # return next frame (full frame)
    return Response(capture.get_frame_sse(), mimetype="text/event-stream")


@app.route("/sbs")
def get_img_sbs():
    # SBS - Session Based Suffering (Streaming)
    # capture.screenshot()
    if "idx" not in session:
        session["idx"] = 0
    frame = capture.get_frame_sbs(session["idx"])
    print(session["idx"])
    session["idx"] = session["idx"] + 1
    return jsonify({"message": frame})


@app.route("/test")
def test():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
