import os
import cv2
import mediapipe as mp
import time
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from flask import Flask, render_template, Response

app = Flask(__name__)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# Volume Control Setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

def detect_gestures():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Camera not detected")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                ring_tip = hand_landmarks.landmark[16]
                pinky_tip = hand_landmarks.landmark[20]

                print(f"Thumb: {thumb_tip.y}, Index: {index_tip.y}, Middle: {middle_tip.y}, Ring: {ring_tip.y}, Pinky: {pinky_tip.y}")

                # Volume Control
                if index_tip.y < thumb_tip.y:
                    print("🔊 Increasing Volume")
                    pyautogui.press("volumeup")

                elif index_tip.y > thumb_tip.y:
                    print("🔉 Decreasing Volume")
                    pyautogui.press("volumedown")

                elif index_tip.y < middle_tip.y < ring_tip.y:
                    print("🔇 Muting/Unmuting Volume")
                    pyautogui.press("volumemute")

                # Open PowerPoint
                if all(f.y < 0.5 for f in [index_tip, middle_tip, ring_tip, pinky_tip]):
                    print("📊 Opening PowerPoint")
                    os.system("start powerpnt")
                    time.sleep(3)

                # Close PowerPoint
                elif all(f.y > 0.6 for f in [index_tip, middle_tip, ring_tip, pinky_tip]):
                    print("❌ Closing PowerPoint")
                    os.system("taskkill /IM POWERPNT.EXE /F")

                # Next Slide
                elif index_tip.x > 0.8:
                    print("➡️ Next Slide")
                    pyautogui.press("right")

                # Previous Slide
                elif index_tip.x < 0.2:
                    print("⬅️ Previous Slide")
                    pyautogui.press("left")

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(detect_gestures(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

