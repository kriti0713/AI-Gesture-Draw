<div align="center">

# 🎨🖐️ AI Gesture Drawing App — Air Canvas Pro

**An interactive, real-time virtual drawing canvas controlled entirely by hand gestures.**

Draw, sketch, erase, render 2D geometric shapes, resize brushes with a pinch, and manage your artwork — all using natural hand gestures captured by your webcam, powered by Python, OpenCV, and MediaPipe.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-00C4B4?style=for-the-badge&logo=google&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Canvas%20Ops-013243?style=for-the-badge&logo=numpy&logoColor=white)

</div>

---

## 📖 Overview

AI Gesture Drawing App replaces the mouse and keyboard with your hands. Using real-time hand landmark detection running in MediaPipe's low-latency `VIDEO` mode, it turns your webcam feed into a fully interactive canvas — draw freehand strokes, build geometric shapes with both hands, resize your brush with a pinch, erase with an open palm, and manage your artwork through an on-screen gesture-driven toolbar, all without touching a physical input device.

---

## 🌟 Features

### ☝️ Gesture-Based Control
| Gesture | Mode | Description |
|---|---|---|
| Index finger up | **Drawing** | Draws smoothed, neon-accented lines on the canvas using the active color |
| Index + middle fingers up | **Hover / Selection** | Moves the cursor without drawing; used to select colors, shapes, and toolbar actions |
| Thumb + index up, pinch in/out | **Pinch Resize** | Adjusts brush thickness dynamically based on pinch distance |
| Open palm (all 5 fingers up) | **Palm Eraser** | Erases a wide circular area centered on your palm |
| Both hands, index fingers up | **Two-Hand Shape Building** | Stretches a live shape preview between both fingertips |
| Pinch while building a shape | **Drop Shape** | Locks the in-progress shape onto the canvas |
| Break pointing pose without pinching | **Cancel Shape** | Discards the in-progress shape instead of committing it |

### 🎨 Interactive Toolbar (on-screen, gesture-controlled)
- **Colors:** Red, Blue, Green, Yellow, Eraser — selected with a fingertip hover, active color highlighted
- **Shapes:** Line, Rectangle, Square, Circle, Triangle, Star — selected from a vertical shape menu
- **Fill toggle** — switch shapes between outlined and solid-filled
- **Background toggle** — draw over your live video feed or on a plain dark canvas
- **Undo / Redo** — step backward and forward through your drawing history
- **Save** — export your canvas as a timestamped PNG, with an on-screen flash confirmation

### 🧹 Canvas Tools
- **Virtual Eraser & Clear Screen** — remove specific strokes or wipe the whole canvas instantly
- **Undo / Redo stack** — full snapshot-based history, not just single-step undo
- **Save Canvas** — export your artwork as a timestamped PNG file at any time

### ⚡ Smooth, Reliable Tracking
- **Line Smoothing** — exponential moving average filtering removes jitter and hand tremors for clean strokes
- **Stabilized Thumb Detection** — distance-based thumb-extension check (rather than simple axis comparison) for more reliable finger-state detection across hand angles
- **Neon Line Rendering** — strokes render with a brighter inner core for a glowing, high-visibility line effect
- **Two-Hand Shape Rendering** — shapes are drawn live between both index fingertips as a real-time preview before being committed

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Computer Vision & Video Processing | OpenCV |
| Hand Landmark Detection | MediaPipe Tasks Vision API (`HandLandmarker`, `VIDEO` running mode) |
| Canvas Matrix Operations | NumPy |

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure Python 3.x is installed, then clone the repository:

```bash
git clone https://github.com/kriti0713/AI-Gesture-Draw.git
cd AI-Gesture-Draw
```

### 2. Install Dependencies

```bash
pip install opencv-python mediapipe numpy
```

*(On Windows, if `pip` isn't recognized, use `py -m pip install opencv-python mediapipe numpy` instead.)*

### 3. Download Model Weights

MediaPipe requires the pretrained `hand_landmarker.task` file:

```bash
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

If `curl` isn't available, paste that URL directly into your browser to download the file, then place it in the **root directory** of this project folder.

---

## 💻 How to Run

```bash
python hand_track.py
```

*(or `py hand_track.py` on Windows)*

---

## 🎮 Controls & Gestures

| Gesture / Key | Action | Description |
|---|---|---|
| ☝️ Index finger up | **Draw** | Draws lines on the canvas using the currently active color and brush size |
| ✌️ Index + middle up | **Hover / Select** | Moves cursor without drawing; hover over toolbar to change colors, shapes, or trigger actions |
| 🤏 Thumb + index up, pinch | **Resize brush** | Adjusts brush size based on the distance between thumb and index finger |
| 🖐️ Open palm | **Palm eraser** | Erases a wide area centered on your palm |
| 🖐️🖐️ Two index fingers up | **Build shape** | Renders the selected shape live between both index fingertips |
| 🤏 Pinch while building | **Drop shape** | Commits the shape onto the canvas at its current position |
| `u` | **Undo** | Reverts the last drawn stroke, shape, or clear action |
| `r` | **Redo** | Re-applies the last undone action |
| `s` | **Save** | Saves the current canvas as a timestamped `.png` file |
| `c` | **Clear canvas** | Instantly clears all drawn strokes from the screen |
| `q` | **Quit** | Closes the application safely |

### On-screen toolbar actions (fingertip hover)
| Button | Description |
|---|---|
| **FILL: ON/OFF** | Toggles between outlined and filled shapes |
| **BG: DARK/VIDEO** | Toggles the canvas background between your live video feed and a plain dark background |
| **UNDO / REDO** | Same as the `u` / `r` keys, triggerable by gesture |
| **CLEAR** | Same as the `c` key, triggerable by gesture |
| **SAVE** | Same as the `s` key, triggerable by gesture, with a flash confirmation |

---

## 📂 Project Structure

```
AI-Gesture-Draw/
│
├── hand_track.py            # Main application script
├── hand_landmarker.task     # MediaPipe landmark detector model (ignored in git)
├── drawing_*.png             # Saved canvas exports (created when saving)
├── .gitignore                 # Git ignore file
└── README.md                  # Project documentation
```

---

## 💡 Tips for Best Results

- **Lighting matters** — face a light source rather than having it behind you; hand tracking is less reliable in backlit or low-light setups.
- **Keep hands centered** in frame when possible — detection accuracy drops near the edges of the camera view.
- **Distance** — keep your hands roughly arm's length from the camera for the most reliable tracking.
- If gestures feel unresponsive or overly sensitive, tune `min_hand_detection_confidence`, `min_tracking_confidence`, and `PINCH_THRESHOLD` near the top of `hand_track.py` to match your setup.

---

## 🗺️ Roadmap

- Web-based version (MediaPipe Tasks Vision JS + HTML5 Canvas) for a browser-based, shareable "portal"
- Adjustable brush textures (dashed lines, glow intensity via pinch)
- Separate outline color vs. fill color for shapes
- Multi-layer canvas support

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/kriti0713/AI-Gesture-Draw/issues) or open a pull request.

---

## 👩‍💻 Author

**Kritika Gupta**
[GitHub](https://github.com/kriti0713) · [LinkedIn](https://www.linkedin.com/in/kritikagupta007) · [Email](mailto:gkritika007@gmail.com)
