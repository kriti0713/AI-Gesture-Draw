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
    running_mode=vision.RunningMode.VIDEO,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
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
brush_thickness = 6

shapes = ["None", "Line", "Rect", "Square", "Circle", "Triangle", "Star"]
shape_mode = "None"
is_filled_shape = False
dark_canvas_mode = False

SHAPE_COL_X = 110
SHAPE_ROW_H = 50
SHAPE_START_Y = 75
TOP_BAR_H = 65
PINCH_THRESHOLD = 40


undo_stack = []
redo_stack = []
MAX_UNDO = 20

drawing_stroke = False
building_shape = False
shape_p1, shape_p2 = None, None
prev_any_pinching = False


last_ui_click_time = 0
UI_COOLDOWN = 0.4  


flash_alpha = 0


def fingers_up(hl):
    """Accurately detects open fingers with stabilized thumb detection."""
    fingers = []
    
   
    thumb_dist = math.hypot(hl[4].x - hl[17].x, hl[4].y - hl[17].y)
    ref_dist = math.hypot(hl[2].x - hl[17].x, hl[2].y - hl[17].y)
    fingers.append(1 if thumb_dist > ref_dist * 1.25 else 0)

   
    tips = [8, 12, 16, 20]
    for tip in tips:
        if hl[tip].y < hl[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def save_undo_state():
    """Saves canvas snapshot to undo stack."""
    global redo_stack
    undo_stack.append(canvas.copy())
    if len(undo_stack) > MAX_UNDO:
        undo_stack.pop(0)
    redo_stack.clear()


def star_points(cx, cy, outer_r, inner_r, rotation=-90):
    pts = []
    for i in range(10):
        angle = math.radians(rotation + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append([int(x), int(y)])
    return np.array(pts, dtype=np.int32)


def draw_shape(target, p1, p2, color, thickness, shape, fill=False):
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    thick = -1 if fill else thickness

    if shape == "Line":
        cv2.line(target, p1, p2, color, thickness)
    elif shape == "Rect":
        cv2.rectangle(target, p1, p2, color, thick)
    elif shape == "Square":
        side = max(abs(x2 - x1), abs(y2 - y1))
        sx = side if x2 >= x1 else -side
        sy = side if y2 >= y1 else -side
        cv2.rectangle(target, p1, (x1 + sx, y1 + sy), color, thick)
    elif shape == "Circle":
        radius = int(math.hypot(x2 - x1, y2 - y1) / 2)
        cv2.circle(target, (cx, cy), radius, color, thick)
    elif shape == "Triangle":
        top = (cx, min(y1, y2))
        bottom_left = (min(x1, x2), max(y1, y2))
        bottom_right = (max(x1, x2), max(y1, y2))
        pts = np.array([top, bottom_left, bottom_right], dtype=np.int32)
        if fill:
            cv2.drawContours(target, [pts], 0, color, -1)
        else:
            cv2.polylines(target, [pts], isClosed=True, color=color, thickness=thickness)
    elif shape == "Star":
        outer_r = int(math.hypot(x2 - x1, y2 - y1) / 2)
        inner_r = int(outer_r * 0.45)
        pts = star_points(cx, cy, outer_r, inner_r)
        if fill:
            cv2.drawContours(target, [pts], 0, color, -1)
        else:
            cv2.polylines(target, [pts], isClosed=True, color=color, thickness=thickness)


def draw_neon_line(img, p1, p2, color, thickness):
    """Draws a line with a bright inner neon core effect."""
    cv2.line(img, p1, p2, color, thickness)
    if thickness > 3 and color != (0, 0, 0):
        core_thick = max(1, thickness // 3)
        cv2.line(img, p1, p2, (255, 255, 255), core_thick)



while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, (1280, 720))
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

  
    ui_overlay = frame.copy()

    
    cv2.rectangle(ui_overlay, (0, 0), (w, TOP_BAR_H), (30, 30, 30), -1)
    color_box_w = 90
    
    color_rects = []
    for i, (col, name) in enumerate(colors):
        x1, y1 = 10 + i * (color_box_w + 8), 8
        x2, y2 = x1 + color_box_w, TOP_BAR_H - 8
        color_rects.append((x1, y1, x2, y2, col, name))
        bg_col = col if name != "Eraser" else (220, 220, 220)
        cv2.rectangle(ui_overlay, (x1, y1), (x2, y2), bg_col, -1)
        
        if (draw_color == col and name != "Eraser") or (draw_color == (0, 0, 0) and name == "Eraser"):
            cv2.rectangle(ui_overlay, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), (0, 255, 255), 3)
        
        lbl = name if name != "Eraser" else "ERASER"
        cv2.putText(ui_overlay, lbl, (x1 + 8, y1 + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0) if name == "Eraser" else (255, 255, 255), 1)

    
    action_buttons = [
        ("FILL: ON" if is_filled_shape else "FILL: OFF", (520, 8, 620, TOP_BAR_H - 8)),
        ("BG: DARK" if dark_canvas_mode else "BG: VIDEO", (630, 8, 730, TOP_BAR_H - 8)),
        ("UNDO", (740, 8, 820, TOP_BAR_H - 8)),
        ("REDO", (830, 8, 910, TOP_BAR_H - 8)),
        ("CLEAR", (920, 8, 1000, TOP_BAR_H - 8)),
        ("SAVE", (1010, 8, 1090, TOP_BAR_H - 8))
    ]
    for label, (x1, y1, x2, y2) in action_buttons:
        cv2.rectangle(ui_overlay, (x1, y1), (x2, y2), (70, 70, 70), -1)
        cv2.rectangle(ui_overlay, (x1, y1), (x2, y2), (200, 200, 200), 1)
        cv2.putText(ui_overlay, label, (x1 + 6, y1 + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

   
    cv2.rectangle(ui_overlay, (0, SHAPE_START_Y - 5), (SHAPE_COL_X + 5, SHAPE_START_Y + len(shapes) * SHAPE_ROW_H + 5), (30, 30, 30), -1)
    shape_rects = []
    for i, name in enumerate(shapes):
        x1, y1 = 5, SHAPE_START_Y + i * SHAPE_ROW_H
        x2, y2 = SHAPE_COL_X, SHAPE_START_Y + (i + 1) * SHAPE_ROW_H - 4
        shape_rects.append((x1, y1, x2, y2, name))
        bg = (60, 180, 60) if name == shape_mode else (70, 70, 70)
        cv2.rectangle(ui_overlay, (x1, y1), (x2, y2), bg, -1)
        cv2.rectangle(ui_overlay, (x1, y1), (x2, y2), (255, 255, 255), 1)
        cv2.putText(ui_overlay, name, (x1 + 8, y1 + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    cv2.addWeighted(ui_overlay, 0.65, frame, 0.35, 0, frame)

    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    timestamp_ms = int(time.time() * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    mode_text = "No Hand"
    hands_list = result.hand_landmarks if result.hand_landmarks else []
    num_detected = len(hands_list)

    fingers_per_hand = [fingers_up(hl) for hl in hands_list]
    pure_point = [f[1] == 1 and f[2] == 0 for f in fingers_per_hand]
    both_pointing = num_detected == 2 and pure_point[0] and pure_point[1]

   
    any_pinching = False
    for h1 in hands_list:
        thumb, index = h1[4], h1[8]
        dist_px = math.hypot((thumb.x - index.x) * w, (thumb.y - index.y) * h)
        if dist_px < PINCH_THRESHOLD:
            any_pinching = True
            break
    pinch_event = any_pinching and not prev_any_pinching

    
    if shape_mode != "None" and building_shape:
        if pinch_event:
            mode_text = "Shape Placed!"
            if shape_p1 and shape_p2:
                save_undo_state()
                draw_shape(canvas, shape_p1, shape_p2, draw_color, brush_thickness, shape_mode, is_filled_shape)
            building_shape = False
            shape_p1, shape_p2 = None, None
        elif both_pointing:
            mode_text = f"Building {shape_mode} (Pinch to Drop)"
            p1 = (int(hands_list[0][8].x * w), int(hands_list[0][8].y * h))
            p2 = (int(hands_list[1][8].x * w), int(hands_list[1][8].y * h))
            shape_p1, shape_p2 = p1, p2
            cv2.circle(frame, p1, 8, (0, 255, 0), -1)
            cv2.circle(frame, p2, 8, (0, 255, 0), -1)
            draw_shape(frame, p1, p2, draw_color, brush_thickness, shape_mode, is_filled_shape)
        else:
            mode_text = "Shape Cancelled"
            building_shape = False
            shape_p1, shape_p2 = None, None
        prev_x, prev_y = 0, 0
        drawing_stroke = False

    elif shape_mode != "None" and both_pointing:
        mode_text = f"Building {shape_mode} (Pinch to Drop)"
        p1 = (int(hands_list[0][8].x * w), int(hands_list[0][8].y * h))
        p2 = (int(hands_list[1][8].x * w), int(hands_list[1][8].y * h))
        shape_p1, shape_p2 = p1, p2
        building_shape = True
        cv2.circle(frame, p1, 8, (0, 255, 0), -1)
        cv2.circle(frame, p2, 8, (0, 255, 0), -1)
        draw_shape(frame, p1, p2, draw_color, brush_thickness, shape_mode, is_filled_shape)
        prev_x, prev_y = 0, 0
        drawing_stroke = False

    
    elif num_detected >= 1:
        hl = hands_list[0]
        fingers = fingers_up(hl)
        index_tip, thumb_tip = hl[8], hl[4]
        cx, cy = int(index_tip.x * w), int(index_tip.y * h)
        tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)

        
        if sum(fingers) == 5:
            mode_text = "Palm Eraser"
            palm_cx, palm_cy = int(hl[9].x * w), int(hl[9].y * h)
            if not drawing_stroke:
                save_undo_state()
                drawing_stroke = True
            cv2.circle(canvas, (palm_cx, palm_cy), 60, (0, 0, 0), -1)
            cv2.circle(frame, (palm_cx, palm_cy), 60, (200, 200, 200), 2)

       
        elif fingers == [1, 1, 0, 0, 0]:
            mode_text = "Resize Brush"
            prev_x, prev_y = 0, 0
            drawing_stroke = False
            
            pinch_dist = math.hypot(tx - cx, ty - cy)
            target_thickness = int(np.interp(pinch_dist, [30, 200], [2, 50]))
            
            
            brush_thickness = int(brush_thickness * 0.75 + target_thickness * 0.25)
            
            mid_x, mid_y = (tx + cx) // 2, (ty + cy) // 2
            cv2.line(frame, (tx, ty), (cx, cy), (255, 255, 255), 2)
            cv2.circle(frame, (mid_x, mid_y), brush_thickness // 2, draw_color, -1)
            cv2.putText(frame, f"Size: {brush_thickness}", (mid_x + 15, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        
        elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0:
            in_ui = False

            
            if cy < TOP_BAR_H:
                in_ui = True
                prev_x, prev_y = 0, 0
                drawing_stroke = False
                
                
                for x1, y1, x2, y2, col, name in color_rects:
                    if x1 <= cx <= x2:
                        draw_color = col
                        brush_thickness = 30 if name == "Eraser" else 6
                        mode_text = f"Selected {name}"
                        cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)
                        break

                
                if time.time() - last_ui_click_time > UI_COOLDOWN:
                    for label, (x1, y1, x2, y2) in action_buttons:
                        if x1 <= cx <= x2 and y1 <= cy <= y2:
                            last_ui_click_time = time.time()
                            if "FILL" in label:
                                is_filled_shape = not is_filled_shape
                            elif "BG" in label:
                                dark_canvas_mode = not dark_canvas_mode
                            elif label == "UNDO" and undo_stack:
                                redo_stack.append(canvas.copy())
                                canvas = undo_stack.pop()
                            elif label == "REDO" and redo_stack:
                                undo_stack.append(canvas.copy())
                                canvas = redo_stack.pop()
                            elif label == "CLEAR":
                                save_undo_state()
                                canvas = np.zeros((h, w, 3), dtype=np.uint8)
                            elif label == "SAVE":
                                filename = f"drawing_{int(time.time())}.png"
                                out_img = canvas.copy() if dark_canvas_mode else cv2.addWeighted(frame, 0.5, canvas, 0.7, 0)
                                cv2.imwrite(filename, out_img)
                                flash_alpha = 1.0

            
            elif cx < SHAPE_COL_X and cy >= SHAPE_START_Y:
                in_ui = True
                prev_x, prev_y = 0, 0
                drawing_stroke = False
                for x1, y1, x2, y2, name in shape_rects:
                    if y1 <= cy <= y2:
                        shape_mode = name
                        mode_text = f"Selected {name}"
                        cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)
                        break

            
            if not in_ui:
                if shape_mode == "None":
                    mode_text = "Eraser" if draw_color == (0, 0, 0) else "Drawing"

                    if prev_x == 0 and prev_y == 0:
                        prev_x, prev_y = cx, cy
                        if not drawing_stroke:
                            save_undo_state()
                            drawing_stroke = True

                    smooth_x = int(prev_x * 0.5 + cx * 0.5)
                    smooth_y = int(prev_y * 0.5 + cy * 0.5)

                    draw_neon_line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), draw_color, brush_thickness)
                    prev_x, prev_y = smooth_x, smooth_y

                    
                    cv2.circle(frame, (cx, cy), brush_thickness // 2 + 4, draw_color, 2)
                    cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)
                else:
                    mode_text = f"Point with 2nd hand to build {shape_mode}"
                    prev_x, prev_y = 0, 0
                    drawing_stroke = False
                    cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)

        else:
            prev_x, prev_y = 0, 0
            drawing_stroke = False
    else:
        prev_x, prev_y = 0, 0
        drawing_stroke = False

    prev_any_pinching = any_pinching

    
    if dark_canvas_mode:
        combined = cv2.addWeighted(np.zeros_like(frame), 1.0, canvas, 1.0, 0)
    else:
        combined = cv2.addWeighted(frame, 0.7, canvas, 0.8, 0)

    
    if flash_alpha > 0:
        flash_overlay = np.full_like(combined, 255)
        combined = cv2.addWeighted(combined, 1.0 - flash_alpha, flash_overlay, flash_alpha, 0)
        flash_alpha = max(0, flash_alpha - 0.15)

    
    cv2.putText(combined, f"Mode: {mode_text}", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(combined, "Touch UI to Select | S:Save | U:Undo | R:Redo | C:Clear | Q:Quit", (320, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    cv2.imshow("Air Canvas Pro", combined)

    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        save_undo_state()
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
    elif key == ord('s'):
        filename = f"drawing_{int(time.time())}.png"
        out_img = canvas.copy() if dark_canvas_mode else cv2.addWeighted(frame, 0.5, canvas, 0.7, 0)
        cv2.imwrite(filename, out_img)
        flash_alpha = 1.0
    elif key == ord('u'):
        if undo_stack:
            redo_stack.append(canvas.copy())
            canvas = undo_stack.pop()
    elif key == ord('r'):
        if redo_stack:
            undo_stack.append(canvas.copy())
            canvas = redo_stack.pop()

cap.release()
cv2.destroyAllWindows()