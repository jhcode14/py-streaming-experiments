from flask import Flask, jsonify, session, make_response, request
from flask_cors import CORS
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hmac
import hashlib
import json
import time
import secrets



app = Flask(__name__)

SIGNATURE = "a-string-secret-at-least-256-bits-long"
SALT = "hello_world_12345_eeee"

db = {} # k=username, v=hash(salted password)

@app.route("/signup", methods=["POST"])
def signup():
    """ Signup
    param: { "username", "password" }

    salted hash
    """

    data = request.get_json()

    # validate params
    if "username" not in data or "password" not in data:
        return "False"
    
    # no signup
    if "username" in db:
        return "False"

    password = data["password"].encode("utf-8")
    salt = secrets.token_bytes(16)
    db[data["username"]] = [hashlib.shake_128(password+salt).digest(20), salt]
    print(db)

    return "True"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    # check creds
    username, password = data["username"], data["password"]
    if username not in db:
        return "False"
    
    calculated_hash = hashlib.shake_128(password.encode("utf-8")+db[username][1]).digest(20)
    if calculated_hash != db[username][0]:
        return "False"
    
    r = make_response("True")
    r.set_cookie(key="auth", value=create_jwt(username), max_age=30, domain="127.0.0.1", path="/", secure=True, httponly=True, samesite="lax")
    return r

def validate_jwt(data) -> bool:
    jwt = data["jwt"].split(".")

    # validate jwt
    b64_header = jwt[0]
    b64_payload = jwt[1]
    signature = jwt[2]

    print(b64_header)
    print(b64_payload)

    digest = hmac.new(SIGNATURE.encode('utf-8'), f"{b64_header}.{b64_payload}".encode('utf-8'), hashlib.sha256).digest()
    if signature != urlsafe_b64encode(digest).decode('utf-8').rstrip("="):
        return False

    # check if expiration
    # Add padding back before decoding
    padded_payload = b64_payload + "=" * (4 - len(b64_payload) % 4)
    payload = json.loads(urlsafe_b64decode(padded_payload).decode("utf-8"))
    if time.time() - payload["iat"] > 30:
        return False
    return True

@DeprecationWarning
@app.route("/jwt", methods=["POST"])
def jwt():
    data = request.get_json()

    # generate & return jwt
    return jsonify({"jwt": create_jwt(data["username"])})


def create_jwt(username: str) -> str:
    header = { "alg": "HS256", "typ": "JWT" }
    payload = { "username": username, "iat": time.time() }

    # turn params to base 64
    b64_header = urlsafe_b64encode(json.dumps(header).encode('utf-8')).decode('utf-8').rstrip("=")
    b64_payload = urlsafe_b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8').rstrip("=")

    # get hmac of b64 header/payload
    digest = hmac.new(SIGNATURE.encode('utf-8'), f"{b64_header}.{b64_payload}".encode('utf-8'), hashlib.sha256).digest()
    digest = urlsafe_b64encode(digest).decode('utf-8').rstrip("=")

    return f"{b64_header}.{b64_payload}.{digest}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)