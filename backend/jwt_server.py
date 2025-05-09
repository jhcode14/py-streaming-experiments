from flask import Flask, jsonify, session, Response, request
from flask_cors import CORS
from base64 import urlsafe_b64encode
import hmac
import hashlib
import json


app = Flask(__name__)

SIGNATURE = "a-string-secret-at-least-256-bits-long"

@app.route("/jwt", methods=["POST"])
def jwt():
    data = request.get_json()
    # TODO: (skip) validate those are valid json objects

    # turn params to base 64
    b64_header = urlsafe_b64encode(json.dumps(data["header"]).encode('utf-8')).decode('utf-8').rstrip("=")
    b64_payload = urlsafe_b64encode(json.dumps(data["payload"]).encode('utf-8')).decode('utf-8').rstrip("=")

    # get hmac of b64 header/payload
    digest = hmac.new(SIGNATURE.encode('utf-8'), f"{b64_header}.{b64_payload}".encode('utf-8'), hashlib.sha256).digest()
    digest = urlsafe_b64encode(digest).decode('utf-8').rstrip("=")

    # generate & return jwt
    return jsonify({"jwt": f"{b64_header}.{b64_payload}.{digest}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)