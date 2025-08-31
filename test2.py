import cv2
import numpy as np
import socket
import time

# === UDP Setup ===
UDP_IP = "192.168.4.1"   # ESP32 IP
UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_cmd(cmd):
    sock.sendto(cmd.encode(), (UDP_IP, UDP_PORT))

# === Camera Setup ===
cap = cv2.VideoCapture(0)

# === PD Control ===
Kp = 0.6
Kd = 0.3
last_error = 0

# === LAB Thresholds (adjust for your track color) ===
lower = np.array([20, 130, 130])   # Example
upper = np.array([255, 180, 180])

def detect_line_roi(frame, roi):
    """Extract line position in ROI"""
    x, y, w, h = roi
    roi_img = frame[y:y+h, x:x+w]
    lab = cv2.cvtColor(roi_img, cv2.COLOR_BGR2LAB)
    mask = cv2.inRange(lab, lower, upper)
    M = cv2.moments(mask)
    cx = None
    if M["m00"] > 0:
        cx = int(M["m10"]/M["m00"]) + x
    return cx, mask

def pd_steering(error):
    global last_error
    derivative = error - last_error
    control = Kp * error + Kd * derivative
    last_error = error
    return control

def detect_cylinder_color(frame):
    """Detects cylinder color in central ROI"""
    h, w, _ = frame.shape
    roi = frame[h//4:h//2, w//3:2*w//3]  # central box
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # red mask
    red1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    red2 = cv2.inRange(hsv, (160, 100, 100), (179, 255, 255))
    red = cv2.bitwise_or(red1, red2)

    # green mask
    green = cv2.inRange(hsv, (40, 100, 100), (90, 255, 255))

    if cv2.countNonZero(red) > 500:  # threshold pixel count
        return "RED"
    elif cv2.countNonZero(green) > 500:
        return "GREEN"
    return None

def go_around(color):
    if color == "RED":
        print("Going around RIGHT")
        send_cmd("RIGHT"); time.sleep(1.0)
        send_cmd("FWD"); time.sleep(1.5)
        send_cmd("LEFT"); time.sleep(1.0)
        send_cmd("FWD"); time.sleep(1.0)
    elif color == "GREEN":
        print("Going around LEFT")
        send_cmd("LEFT"); time.sleep(1.0)
        send_cmd("FWD"); time.sleep(1.5)
        send_cmd("RIGHT"); time.sleep(1.0)
        send_cmd("FWD"); time.sleep(1.0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # === Define ROIs ===
    top_roi = (int(0.2*w), int(0.2*h), int(0.6*w), int(0.1*h))
    mid_roi = (int(0.3*w), int(0.5*h), int(0.4*w), int(0.1*h))
    bot_roi = (int(0.1*w), int(0.8*h), int(0.8*w), int(0.1*h))

    # Detect line in ROIs
    cx_top, mask_top = detect_line_roi(frame, top_roi)
    cx_mid, mask_mid = detect_line_roi(frame, mid_roi)
    cx_bot, mask_bot = detect_line_roi(frame, bot_roi)

    # Pick bottom ROI as main steering reference
    if cx_bot is not None:
        error = (w//2) - cx_bot
        control = pd_steering(error)
        if control > 20:
            send_cmd("LEFT")
        elif control < -20:
            send_cmd("RIGHT")
        else:
            send_cmd("FWD")
    else:
        send_cmd("STOP")

    # === Cylinder detection ===
    color = detect_cylinder_color(frame)
    if color is not None:
        go_around(color)

    # Show debug
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
