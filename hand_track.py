import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

canvas = None
prev_x, prev_y = 0, 0

colors = [
    ((0, 0, 255), "Red"),
    ((255, 0, 0), "Blue"),
    ((0, 255, 0), "Green"),
    ((0, 255, 255), "Yellow"),
    ((0, 0, 0), "Eraser")
]
draw_color = colors[0][0]
brush_thickness = 5

def fingers_up(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    if hand_landmarks[tips[0]].x < hand_landmarks[tips[0]- 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip_id in tips[1:]:
        if hand_landmarks[tip_id].y < hand_landmarks[tip_id - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers                     

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, (1280, 720))    

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros((h, w, 3), dtype = np.uint8)

    box_w = w // len(colors)
    for i, (col, name) in enumerate(colors):
        x1, y1 = i * box_w, 0
        x2, y2 = (i + 1) * box_w, 60

        if name == "Eraser":
            cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), -1)
            cv2.putText(frame, "ERASER", (x1 + 15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)    
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), col, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = detector.detect(mp_image)

    mode_text = "No Hand"

    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:
            index_tip = hand_landmarks[8]
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)

            fingers = fingers_up(hand_landmarks)

            if fingers[1] == 1 and fingers[2] == 1:
                mode_text = "Hover/Select"
                prev_x, prev_y = 0,0

                if cy < 60:
                    selected_idx = cx // box_w
                    if selected_idx < len(colors):
                        draw_color = colors[selected_idx][0]
                        brush_thickness = 30 if colors[selected_idx][1] == "Eraser" else 5

                cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)  

            elif fingers[1] == 1 and fingers[2] == 0:
                mode_text = "Eraser" if draw_color == (0, 0, 0) else "Drawing"

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = cx, cy

                smooth_x = int(prev_x * 0.6 + cx * 0.4)
                smooth_y = int(prev_y * 0.6 + cy * 0.4)    

                cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), draw_color, brush_thickness)
                prev_x, prev_y = smooth_x, smooth_y

                cv2.circle(frame, (cx, cy), 10, draw_color, -1)

            else:
                mode_text = "Idle"
                prev_x, prev_y = 0, 0     


    else:
        prev_x, prev_y = 0, 0

    combined = cv2.addWeighted(frame, 0.7, canvas, 0.7, 0)
    cv2.putText(combined, f"Mode: {mode_text}", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.imshow("Gesture Drawing", combined)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros((h, w, 3), dtype=np.uint8)    

cap.release()
cv2.destroyAllWindows()