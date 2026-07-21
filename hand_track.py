import cv2
import time
import math
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    num_hands=2,
    running_mode = vision.RunningMode.VIDEO,
    min_hand_detection_confidence = 0.5,
    min_hand_presence_confidence = 0.5,
    min_tracking_confidence = 0.5
)
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

shapes = ["None", "Line", "React", "Square", "Circle", "Triangle", "Star"]
shape_mode = "None"

SHAPE_COL_X = 100
SHAPE_ROW_H = 55
SHAPE_START_Y = 60

undo_stack = []
MAX_UNDO = 20

drawing_stroke = False
shape_active = False
shape_p1, shape_p2 = None, None

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

def save_undo_state():
    undo_stack.append(canvas.copy())
    if len(undo_stack) > MAX_UNDO:
        undo_stack.pop(0)    


def star_points(cx, cy, outer_r, inner_r, rotation = -90):
    pts = []
    for i in range(10):
        angle = math.radians(rotation + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append([int(x), int(y)])
    return np.array(pts, dtype = np.int32)  

def draw_shape(target, p1, p2, color, thickness, shape):
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = (x1 + x2)  // 2, (y1 + y2) // 2    

    if shape == "Line":
       cv2.Line(target, p1, p2, color, thickness)

    elif shape == "Rect":
        cv2.rectangle(target, p1, p2, color, thickness)

    elif shape == "Square":
        side = max(abs(x2 - x1), abs(y2 - y1))
        sx = side if x2 >= x1 else -side
        sy = side if y2 >= y1 else -side
        cv2.rectangle(target, p1, (x1 + sx, y1 + sy), color, thickness)

    elif shape == "Circle":
        radius = int(math.hypot(x2 - x1, y2 - y1) / 2)
        cv2.circle(target, (cx, cy), radius, color, thickness)

    elif shape == "Triangle":
        top = (cx, min(y1, y2))
        bottom_left = (min(x1, x2), max(y1, y2))
        bottom_right = (max(x1, x2), max(y1, y2))
        pts = np.array([top, bottom_left, bottom_right], dtype=np.int32)
        cv2.polylines(target, [pts], isClosed=True, color=color, thickness=thickness)

    elif shape == "Star":
        outer_r = int(math.hypot(x2 - x1, y2 - y1) / 2)
        inner_r = int(outer_r * 0.45)
        pts = star_points(cx, cy, outer_r, inner_r)
        cv2.polylines(target, [pts], isClosed=True, color=color, thickness=thickness)                                                    

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

    for i, name in enumerate(shapes):
        x1, y1 = 0, SHAPE_START_Y + i * SHAPE_ROW_H
        x2, y2 = SHAPE_COL_X, SHAPE_START_Y + (i + 1) * SHAPE_ROW_H
        bg = (100, 100, 100) if name != shape_mode else (60, 180, 60)
        cv2.rectangle(frame, (x1, y1), (x2, y2), bg, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.putText(frame, name, (x1 + 8, y1 + 34), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)    

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    timestamp_ms = int(time.time() * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    mode_text = "No Hand"
    hands_list = result.hand_landmarks if result.hand_landmarks else []
    num_detected = len(hands_list)

    both_pointing = False
    if num_detected == 2:
        f0 = fingers_up(hands_list[0])
        f1 = fingers_up(hands_list[1])
        both_pointing = (f0[1] == 1) and (f1[1] == 1)

    if shape_mode != "None" and num_detected == 2:
        mode_text = f"Building {shape_mode}"
        p1_lm = hands_list[0][8]
        p2_lm = hands_list[1][8]
        p1 = (int(p1_lm.x * w), int(p1_lm.y * h))
        p2 = (int(p2_lm.x * w), int(p2_lm.y * h))

        shape_p1, shape_p2 = p1, p2
        shape_active = True

        cv2.circle(frame, p1, 10, (0, 255, 0), -1)
        cv2.circle(frame, p2, 10, (0, 255, 0), -1)
        draw_shape(frame, p1, p2, draw_color, brush_thickness, shape_mode)  

        prev_x, prev_y = 0, 0
        drawing_stroke = False

    else:
        if shape_active:
            if shape_p1 and shape_p2:
                save_undo_state()
                draw_shape(canvas, shape_p1, shape_p2, draw_color, brush_thickness, shape_mode)
            shape_active = False
            shape_p1, shape_p2 = None, None

        if num_detected >= 1:
            hand_landmarks = hands_list[0]
            index_tip = hand_landmarks[8]
            thumb_tip = hand_landmarks[4]
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)
            tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)

            fingers = fingers_up(hand_landmarks)
            in_shape_col = cx < SHAPE_COL_X and cy >= SHAPE_START_Y

            if fingers[1] == 1 and fingers[2] == 1:
                mode_text = "Hover/Select"
                prev_x, prev_y = 0,0
                drawing_stroke = False

                if cy < 60:
                    idx = cx // box_w
                    if idx < len(colors):
                        draw_color = colors[idx][0]
                        brush_thickness = 30 if colors[idx][1] == "Eraser" else 5
                elif in_shape_col:
                    idx = (cy - SHAPE_START_Y) // SHAPE_ROW_H
                    if 0 <= idx < len(shapes):
                        shape_mode = shapes[idx]      

                cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)  

            elif fingers[1] == 1 and fingers[0] == 1 and fingers[2] == 0:
                mode_text = "Resize Brush" 
                prev_x, prev_y = 0, 0
                drawing_stroke = False

                pinch_dist = math.hypot(tx - cx, ty - cy)
                brush_thickness = int(np.interp(pinch_dist, [20, 200], [2, 50]))
                brush_thickness = max(2, min(brush_thickness, 50))

                mid_x, mid_y = (tx + cx) // 2, (ty + cy) // 2
                cv2.line(frame, (tx, ty), (cx, cy), (255, 255, 255), 2)
                cv2.circle(frame, (mid_x, mid_y), brush_thickness // 2 + 2, draw_color, -1)
                cv2.putText(frame, f"Size: {brush_thickness}", (mid_x + 20, mid_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            elif fingers[1] == 1 and fingers[2] == 0 and shape_mode == "None":
                mode_text = "Eraser" if draw_color == (0, 0, 0) else "Drawing"                

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = cx, cy
                    if not drawing_stroke:
                        save_undo_state()
                        drawing_stroke = True

                smooth_x = int(prev_x * 0.6 + cx * 0.4)
                smooth_y = int(prev_y * 0.6 + cy * 0.4)    

                cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), draw_color, brush_thickness)
                prev_x, prev_y = smooth_x, smooth_y

                cv2.circle(frame, (cx, cy), 10, draw_color, -1)

            elif fingers[1] == 1 and fingers[2] == 0 and shape_mode != "None":
                mode_text = f"Point with 2nd hand too ({shape_mode})"
                prev_x, prev_y = 0, 0
                drawing_stroke = False
                cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)    

            else:
                mode_text = "Idle"
                prev_x, prev_y = 0, 0 
                drawing_stroke = False    


        else:
            prev_x, prev_y = 0, 0
            drawing_stroke = False

    combined = cv2.addWeighted(frame, 0.7, canvas, 0.7, 0)
    cv2.putText(combined, f"Mode: {mode_text}", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.putText(combined, "S:Save  U:Undo  C:Clear  Q:Quit", (20, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.imshow("Gesture Drawing", combined)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros((h, w, 3), dtype=np.uint8)    
    elif key == ord('s'):
        filename = f"drawing_{int(time.time())}.png"
        cv2.imwrite(filename, canvas)
        print(f"Saved as {filename}")
    elif key == ord('u'):
        if undo_stack:
            canvas = undo_stack.pop()        

cap.release()
cv2.destroyAllWindows()