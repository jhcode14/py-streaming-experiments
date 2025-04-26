from flask import Flask, jsonify, session, Response
from flask_sock import Sock
from flask_cors import CORS
from capture import Capture
import time

app = Flask(__name__)
sock = Sock(app)

CORS(app)

capture = Capture()

@sock.route('/video')
def video(ws):
    """
    WebSocket server for video streaming.
    """
    while True:
        index = ws.receive()
        print(index)
        time.sleep(0.02)
        ws.send(capture.get_frame_ws(int(index)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)