import cv2
import mediapipe as mp
import os
import time
import pyautogui  # For controlling keyboard actions

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Track PowerPoint process state
ppt_open = False

def detect_gesture(landmarks):
    """
    Detects hand gestures: Open Palm, Closed Fist, Swipe Right, Swipe Left.
    """
    index_tip = landmarks[8].x
    index_base = landmarks[5].x
    middle_tip = landmarks[12].x
    middle_base = landmarks[9].x
    ring_tip = landmarks[16].x
    ring_base = landmarks[13].x
    pinky_tip = landmarks[20].x
    pinky_base = landmarks[17].x
    thumb_tip = landmarks[4].x
    thumb_base = landmarks[2].x

    # Open Palm: All fingers extended
    if (landmarks[8].y < landmarks[6].y and 
        landmarks[12].y < landmarks[10].y and 
        landmarks[16].y < landmarks[14].y and 
        landmarks[20].y < landmarks[18].y and 
        abs(thumb_tip - thumb_base) > 0.1):  # Thumb spread out
        return "Open Palm"

    # Closed Fist: All fingers folded
    if (landmarks[8].y > landmarks[6].y and 
        landmarks[12].y > landmarks[10].y and 
        landmarks[16].y > landmarks[14].y and 
        landmarks[20].y > landmarks[18].y and 
        abs(thumb_tip - thumb_base) < 0.02):  # Thumb close to palm
        return "Closed Fist"

    # Swipe Right (Next Slide): Index finger moves significantly to the right
    if (index_tip - index_base > 0.1 and 
        middle_tip - middle_base > 0.1 and 
        ring_tip - ring_base > 0.1 and 
        pinky_tip - pinky_base > 0.1):
        return "Swipe Right"

    # Swipe Left (Previous Slide): Index finger moves significantly to the left
    if (index_tip - index_base < -0.1 and 
        middle_tip - middle_base < -0.1 and 
        ring_tip - ring_base < -0.1 and 
        pinky_tip - pinky_base < -0.1):
        return "Swipe Left"

    return "Unknown"

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip for mirror effect
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
    results = hands.process(rgb_frame)  # Process frame with MediaPipe

    gesture = "No Hand Detected"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_gesture(hand_landmarks.landmark)

            if gesture == "Open Palm" and not ppt_open:
                print("🟢 Opening PowerPoint...")
                os.system("start powerpnt")  # Open PowerPoint
                time.sleep(2)  # Wait for PowerPoint to load
                pyautogui.press("f5")  # Start slideshow
                ppt_open = True
                time.sleep(1)

            elif gesture == "Closed Fist" and ppt_open:
                print("🔴 Closing PowerPoint...")
                os.system("taskkill /f /im POWERPNT.EXE")
                ppt_open = False
                time.sleep(1)

            elif gesture == "Swipe Right" and ppt_open:
                print("➡️ Next Slide")
                pyautogui.press("right")  # Move to the next slide
                time.sleep(1)

            elif gesture == "Swipe Left" and ppt_open:
                print("⬅️ Previous Slide")
                pyautogui.press("left")  # Move to the previous slide
                time.sleep(1)

    # Display detected gesture on screen
    cv2.putText(frame, f"Gesture: {gesture}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
# The code snippet above demonstrates how to control PowerPoint slides using hand gestures.
