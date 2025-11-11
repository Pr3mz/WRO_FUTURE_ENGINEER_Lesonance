🚗 Traffic Sign Detection Robot (ESP32 + OpenCV)
📘 Overview

This project is a vision-based autonomous robot built using OpenCV and ESP32 communication.
The robot detects red and green rectangular boxes in real time using a USB camera.
Depending on the detected color:

🟥 Red Box → Turn Right

🟩 Green Box → Turn Left
When no color box is detected, the robot continues to move forward.

Although this project doesn’t use deep learning, it demonstrates computer vision automation and UDP-based robot control.

🧠 System Concept

Camera (USB / Raspberry Pi) captures live video.

OpenCV (Python) processes each frame and detects colored boxes based on HSV ranges.

Detected color and shape trigger commands.

ESP32 receives commands through UDP and controls the robot’s DC motors accordingly.

⚙️ Hardware Requirements

Raspberry Pi or PC (running OpenCV)

ESP32 (connected via Wi-Fi)

2 DC Motors + Motor Driver (e.g., L298N)

USB Camera

Power Source (battery pack)

💻 Software Requirements

Python 3.9 or newer

Libraries:

pip install opencv-python numpy


ESP32 configured as a UDP receiver (listening on port 4210)

🧩 Project Files

main.py – Core computer vision script

ESP32 UDP listener code – Handles received commands (“FWD”, “LEFT”, “RIGHT”, “STOP”)

README.md – Documentation file

🔍 How It Works

OpenCV converts each camera frame into the HSV color space.

Two color masks are created:

Red (two hue ranges)

Green

The code finds contours and approximates shapes to detect rectangles.

When a colored rectangle is found in the center of the frame:

Stops the robot

Turns based on the color

Resumes forward movement

🧪 Commands Sent to ESP32
Command	Description
FWD	Move forward
LEFT	Turn left
RIGHT	Turn right
STOP	Stop motors
🧭 HSV Calibration

If detection fails in low light or on different cameras, tune HSV values inside:

COLOR_RANGES = {
    "RED1": ((0, 120, 70), (10, 255, 255)),
    "RED2": ((170, 120, 70), (180, 255, 255)),
    "GREEN": ((40, 40, 40), (85, 255, 255))
}


Use cv2.imshow() to visualize color masks and fine-tune thresholds for better accuracy.

🚀 Future Improvements

Replace color-based logic with AI object detection (YOLO / TensorFlow Lite)

Implement obstacle avoidance using ultrasonic sensors

Add lane following via line detection

Use PID control for smoother turns

📚 Summary

This project showcases a simple yet effective rule-based autonomous driving system using OpenCV and ESP32.
It’s an ideal foundation for robotics competitions like WRO Future Engineer, where you can later extend it with AI vision or advanced navigation.
