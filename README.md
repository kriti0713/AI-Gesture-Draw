AI Gesture Drawing App 🎨🖐️
An interactive, real-time virtual drawing canvas built using Python, OpenCV, and MediaPipe. Draw, sketch, erase, render 2D geometric shapes, and select colors on your screen using natural hand gestures captured by your webcam!

🌟 Features
☝️ Gesture-Based Control:

Drawing Mode: Lift only your index finger to draw.

Hover / Selection Mode: Lift index + middle fingers to move your cursor without drawing or to select colors and shapes.

Pinch Resize Mode: Pinch thumb and index finger together to adjust brush thickness dynamically.

Two-Hand Shape Mode: Point with index fingers on both hands simultaneously to span and render 2D geometric shapes.

🎨 Interactive Color & Shape Palette:

Colors: Red, Blue, Green, Yellow, and Eraser.

Shapes: Lines, Rectangles, Squares, Circles, Triangles, and Stars.

🧹 Virtual Eraser & Clear Screen: Wipe out specific drawing errors using the Eraser tool, or clear the entire canvas with a single keypress.

↩️ Undo Functionality: Save canvas snapshots to easily revert recent strokes or shapes.

💾 Save Canvas: Save your artwork directly to your disk as a timestamped PNG file.

⚡ Line Smoothing: Employs exponential moving average filtering to remove jitter and hand tremors for clean, smooth strokes.

📐 Full-Screen Canvas Scaling: Automatically resizes and scales high-resolution video streams (1280x720 HD).

🛠️ Tech Stack
Python 3.x

OpenCV (Computer Vision & Video Processing)

MediaPipe Tasks Vision API (Hand Landmark Detection)

NumPy (Canvas Matrix Operations)

🚀 Getting Started
Follow these steps to set up and run the project on your local machine.

1. Prerequisites
Make sure you have Python installed. Clone this repository and navigate to the project directory:

git clone https://github.com/kriti0713/AI-Gesture-Draw.git
cd AI-Gesture-Draw

2. Install DependenciesInstall all required libraries using pip:Bashpip install opencv-python mediapipe numpy
3. Download Model WeightsMediaPipe requires the pretrained hand_landmarker.task file:Download hand_landmarker.task from the official MediaPipe Documentation.Place the hand_landmarker.task file directly in the root directory of this project folder.💻 How to RunRun the script from your terminal:Bashpython hand_track.py
🎮 Controls & GesturesGesture / KeyActionDescription☝️ Index Finger UpDrawDraws lines on the canvas using the currently active color.✌️ Index + Middle UpHover / SelectMoves cursor without drawing. Hover over palette options to change tools/colors/shapes.🤏 Thumb + Index PinchResize BrushAdjust brush size by changing the distance between thumb and index finger.🖐️🖐️ Two Index Fingers UpBuild ShapeRenders selected shape between both index fingertips in real-time.u (Keyboard)UndoReverts the last drawn stroke or shape.s (Keyboard)SaveSaves the current canvas state as a .png file.c (Keyboard)Clear CanvasInstantly clears all drawn strokes from the screen.q (Keyboard)QuitCloses the application safely.📂 Project StructurePlaintextAI-Gesture-Draw/
│
├── hand_track.py            # Main application script
├── hand_landmarker.task     # MediaPipe landmark detector model (ignored in git)
├── .gitignore               # Git ignore file
└── README.md                # Project documentation
