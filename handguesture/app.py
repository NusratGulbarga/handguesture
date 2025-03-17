import os
import cv2
import mediapipe as mp
import time
import pyautogui  # For controlling keyboard
from flask import Flask, render_template, Response

app = Flask(__name__)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

prev_x = None  # Store previous X position of hand

def detect_gestures():
    global prev_x

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Camera not detected")
            break

        frame = cv2.flip(frame, 1)  # Mirror effect
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                ring_tip = hand_landmarks.landmark[16]
                pinky_tip = hand_landmarks.landmark[20]
                palm_base = hand_landmarks.landmark[0]

                current_x = index_tip.x  # Track X position of index finger

                # Open PowerPoint
                if all(f.y < 0.5 for f in [index_tip, middle_tip, ring_tip, pinky_tip]):
                    print("📊 Opening PowerPoint")
                    os.system("start powerpnt")
                    time.sleep(3)

                # Close PowerPoint
                elif all(f.y > 0.6 for f in [index_tip, middle_tip, ring_tip, pinky_tip]):
                    print("❌ Closing PowerPoint")
                    os.system("taskkill /IM POWERPNT.EXE /F")

                # Slide Navigation
                if prev_x is not None:
                    if current_x - prev_x > 0.1:  # Right swipe
                        print("➡️ Next Slide")
                        pyautogui.press("right")
                        time.sleep(1)
                    elif prev_x - current_x > 0.1:  # Left swipe
                        print("⬅️ Previous Slide")
                        pyautogui.press("left")
                        time.sleep(1)
                prev_x = current_x

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
