from flask import Flask, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, port=3000)
socketio.init_app(app, cors_allowed_origins="*")

CORS(app)

room_name_to_user_ids = defaultdict(set)
user_id_to_room = {}

@socketio.on('join')
def join(room_name):
    print(f"handling join room for {request.sid} to room {room_name}")
    join_room(room_name)
    print(f"Current users in room {room_name}: {room_name_to_user_ids[room_name]}")
    socketio.emit("peers", list(room_name_to_user_ids[room_name]), to=request.sid)
    room_name_to_user_ids[room_name].add(request.sid)
    user_id_to_room[request.sid] = room_name
    print(f"Added {request.sid} to room {room_name}")

@socketio.on('sendOffer')
def transport_offer(id, offer):
    print(f"Handling sendOffer from {request.sid} to {id}")
    socketio.emit("offer", (request.sid, offer), to=id)
    print(f"Sent offer from {request.sid} to {id}")
    
@socketio.on('sendAnswer')
def transport_answer(id, answer):
    print(f"Handling sendAnswer from {request.sid} to {id}")
    socketio.emit("answer", (request.sid, answer), to=id)
    print(f"Sent answer from {request.sid} to {id}")

@socketio.on('disconnect')
def handle_disconnection(reason):
    print(f"User {request.sid} disconnected, reason: {reason}")
    room_name = user_id_to_room.get(request.sid)
    if room_name:
        print(f"Broadcasting disconnect for {request.sid} from room {room_name}")
        socketio.emit("someoneDisconnected", request.sid, to=room_name)
        room_name_to_user_ids[room_name].remove(request.sid)
        print(f"Remaining users in room {room_name}: {room_name_to_user_ids[room_name]}")
        del user_id_to_room[request.sid]
    else:
        print(f"No room found for user {request.sid}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3000)