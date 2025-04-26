from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import pyautogui
import base64
import io
import threading

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def update_img():
    cur_img.flush()
    # threading.Timer(3, update_img).start()
    img = pyautogui.screenshot()
    img.save(cur_img, format="PNG")


@app.get("/")
def get_img():
    # update_img()
    cur_img = io.BytesIO()
    img = pyautogui.screenshot()
    img.save(cur_img, format="PNG")
    # return Response(content=img.tobytes(), media_type="image/png")
    return {"message": base64.b64encode(cur_img.getvalue())}


@app.get("/test")
def test():
    return {"message": "Hello World"}


@app.get("/screenshot")
def screenshot():
    img = pyautogui.screenshot()
    img.save("screenshot.png")
    return {"message": "Screenshot saved"}
