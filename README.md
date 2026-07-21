<div align="center">

# 🎨🖐️ AI Gesture Drawing App

**An interactive, real-time virtual drawing canvas controlled entirely by hand gestures.**

Draw, sketch, erase, render 2D geometric shapes, and pick colors on screen — all using natural hand gestures captured by your webcam, powered by Python, OpenCV, and MediaPipe.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-00C4B4?style=for-the-badge&logo=google&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Canvas%20Ops-013243?style=for-the-badge&logo=numpy&logoColor=white)

</div>

---

## 📖 Overview

AI Gesture Drawing App replaces the mouse and keyboard with your hands. Using real-time hand landmark detection, it turns your webcam feed into a fully interactive canvas — draw freehand strokes, build geometric shapes with both hands, resize your brush with a pinch, and manage your artwork, all without touching a physical input device.

---

## 🌟 Features

### ☝️ Gesture-Based Control
| Gesture | Mode | Description |
|---|---|---|
| Index finger up | **Drawing** | Draws lines on the canvas using the active color |
| Index + middle fingers up | **Hover / Selection** | Moves the cursor without drawing; used to select colors or shapes |
| Thumb + index pinch | **Pinch Resize** | Adjusts brush thickness dynamically based on pinch distance |
| Both index fingers up (two hands) | **Two-Hand Shape** | Spans and renders a 2D geometric shape between both fingertips in real time |

### 🎨 Interactive Color & Shape Palette
- **Colors:** Red, Blue, Green, Yellow, Eraser
- **Shapes:** Lines, Rectangles, Squares, Circles, Triangles, Stars

### 🧹 Canvas Tools
- **Virtual Eraser & Clear Screen** — remove specific strokes or wipe the whole canvas instantly
- **Undo** — save canvas snapshots to revert recent strokes or shapes
- **Save Canvas** — export your artwork as a timestamped PNG file

### ⚡ Smooth, Reliable Tracking
- **Line Smoothing** — exponential moving average filtering removes jitter and hand tremors for clean strokes
- **Full-Screen Canvas Scaling** — automatically resizes and scales high-resolution video streams (1280×720 HD)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Computer Vision & Video Processing | OpenCV |
| Hand Landmark Detection | MediaPipe Tasks Vision API |
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

### 3. Download Model Weights

MediaPipe requires the pretrained `hand_landmarker.task` file:

1. Download `hand_landmarker.task` from the [official MediaPipe documentation](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
2. Place it in the **root directory** of this project folder

---

## 💻 How to Run

```bash
python hand_track.py
```

---

## 🎮 Controls & Gestures

| Gesture / Key | Action | Description |
|---|---|---|
| ☝️ Index finger up | **Draw** | Draws lines on the canvas using the currently active color |
| ✌️ Index + middle up | **Hover / Select** | Moves cursor without drawing; hover over palette to change tools/colors/shapes |
| 🤏 Thumb + index pinch | **Resize brush** | Adjusts brush size based on the distance between thumb and index finger |
| 🖐️🖐️ Two index fingers up | **Build shape** | Renders the selected shape between both index fingertips in real time |
| `u` | **Undo** | Reverts the last drawn stroke or shape |
| `s` | **Save** | Saves the current canvas as a `.png` file |
| `c` | **Clear canvas** | Instantly clears all drawn strokes from the screen |
| `q` | **Quit** | Closes the application safely |

---

## 📂 Project Structure

```
AI-Gesture-Draw/
│
├── hand_track.py            # Main application script
├── hand_landmarker.task     # MediaPipe landmark detector model (ignored in git)
├── .gitignore                # Git ignore file
└── README.md                 # Project documentation
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/kriti0713/AI-Gesture-Draw/issues) or open a pull request.

---

## 👩‍💻 Author

**Kritika Gupta**
[GitHub](https://github.com/kriti0713) · [LinkedIn](https://www.linkedin.com/in/kritikagupta007) · [Email](mailto:gkritika007@gmail.com)
