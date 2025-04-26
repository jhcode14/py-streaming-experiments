from flask import Flask
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
from capture import Capture
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, port=3000)
socketio.init_app(app, cors_allowed_origins="*")

CORS(app)

capture = Capture()

@socketio.on('message')
def video(msg):
    """
    WebSocket server for video streaming.
    """
    if msg == "start":
        
        # send data
        for i in range(capture.get_frame_len()):
            time.sleep(0.02)
            send(capture.get_frame_ws(i))

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3000)