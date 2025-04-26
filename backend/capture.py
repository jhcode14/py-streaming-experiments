import pyautogui
import io
import base64
import numpy as np
from PIL import Image
from threading import Lock
import cv2
import time

lock = Lock()


class Capture:
    def __init__(self):
        self.cur_img_bytes = io.BytesIO()
        self.prev_img_bytes = io.BytesIO()
        self.is_first_img = True

        self.frames = self.video_to_PIL("video.mp4")
        self.frame_idx = 0
        self.frame_len = len(self.frames)
        # self._render_encoded_frames()
        # self.frame_len = len(self.encoded_frames)

    def get_frame_len(self):
        return self.frame_len

    def _render_encoded_frames(self):
        # pre-render encoded frames
        self.encoded_frames = []

        self.frames[0].save(self.prev_img_bytes, format="PNG")

        self.encoded_frames.append(
            base64.b64encode(self.prev_img_bytes.getvalue()).decode("ascii")
        )

        for frame in self.frames[1:]:
            frame.save(self.cur_img_bytes, format="PNG")
            self.encoded_frames.append(self.get_diff_img())
            self.prev_img_bytes.flush()
            self.prev_img_bytes.seek(0)
            self.prev_img_bytes.write(self.cur_img_bytes.getvalue())
            self.cur_img_bytes.flush()
            self.cur_img_bytes.seek(0)

    def cv2_to_pil(self, cv2_image):
        """Converts a cv2 image (BGR format) to a PIL Image (RGB format)."""
        cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv2_image_rgb)
        return pil_image

    def video_to_PIL(self, video_path):
        video_capture = cv2.VideoCapture(video_path)
        if not video_capture.isOpened():
            raise Exception(f"Could not open video file: {video_path}")

        pil_images = []
        success, frame = video_capture.read()
        while success:
            pil_image = self.cv2_to_pil(frame)
            pil_images.append(pil_image)
            success, frame = video_capture.read()

        video_capture.release()
        return pil_images

    def screenshot(self):
        with lock:
            self.prev_img_bytes.flush()
            self.prev_img_bytes.seek(0)
            self.prev_img_bytes.write(self.cur_img_bytes.getvalue())

            self.cur_img_bytes.flush()
            self.cur_img_bytes.seek(0)

            img = pyautogui.screenshot(region=(0, 0, 300, 400))
            img.save(self.cur_img_bytes, format="PNG")

    def updateFrame(self):
        """
        with lock:
            self.prev_img_bytes.flush()
            self.prev_img_bytes.seek(0)
            self.prev_img_bytes.write(self.cur_img_bytes.getvalue())

            self.cur_img_bytes.flush()
            self.cur_img_bytes.seek(0)

            img = self.frames[self.frame_idx]
            img.save(self.cur_img_bytes, format="PNG")
            self.frame_idx += 1
            if self.frame_idx >= len(self.frames):
                self.frame_idx = 0
        """
        return

    def get_frame_sbs(self, idx):
        return self.encoded_frames[idx]

    def get_frame_sse(self):
        while True:
            for frame in self.frames:
                try:
                    # Create a new BytesIO object for each frame
                    buffer = io.BytesIO()
                    frame.save(buffer, format="PNG")
                    frame_data = base64.b64encode(buffer.getvalue()).decode("ascii")
                    yield f"data: {frame_data}\n\n"
                    time.sleep(0.02)
                except Exception as e:
                    print(f"Error in get_frame_sse: {e}")
                finally:
                    buffer.close()

    def get_frame_ws(self, idx):
        buffer = io.BytesIO()
        self.frames[idx].save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")

    def get_diff_img(self):
        # expect img to be the same shape
        img1 = np.frombuffer(self.cur_img_bytes.getvalue(), dtype=np.uint8)
        img2 = np.frombuffer(self.prev_img_bytes.getvalue(), dtype=np.uint8)
        img1 = np.resize(img1, img2.shape)
        # print(img1.shape)
        # print(img2.shape)
        xored = np.bitwise_xor(img1, img2)
        # print(xored.shape)
        return base64.b64encode(xored.tobytes()).decode("ascii")

    def get_encoded_img_str(self):
        if self.is_first_img:
            self.is_first_img = False
            return base64.b64encode(self.cur_img_bytes.getvalue()).decode("ascii")
        else:
            return self.get_diff_img()
