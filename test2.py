import cv2
import numpy as np
import socket
import time

# --- UDP Setup ---
ESP32_IP = "192.168.4.1"
ESP32_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_cmd(cmd):
    sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))

# --- Camera Setup ---
cap = cv2.VideoCapture(1)

# --- HSV Ranges (tuned for your dark red block) ---
COLOR_RANGES = {
    # Darker and broader red range
    "RED1": ((0, 90, 60), (15, 255, 255)),
    "RED2": ((160, 80, 60), (180, 255, 255)),
    "GREEN": ((40, 40, 40), (85, 255, 255))
}

KERNEL = np.ones((5,5), np.uint8)

def clean_mask(mask):
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)
    return mask

def detect_boxes(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    red_mask = cv2.bitwise_or(
        cv2.inRange(hsv, *COLOR_RANGES["RED1"]),
        cv2.inRange(hsv, *COLOR_RANGES["RED2"])
    )
    red_mask = clean_mask(red_mask)
    green_mask = clean_mask(cv2.inRange(hsv, *COLOR_RANGES["GREEN"]))

    detections = []
    for color, mask in [("RED", red_mask), ("GREEN", green_mask)]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if area < 1000:
                continue

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(approx)
                M = cv2.moments(c)
                if M["m00"] == 0:
                    continue
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                detections.append((color, (cx, cy), (x, y, w, h)))
    return detections

# --- Main Loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    detections = detect_boxes(frame)
    action = "FWD"

    if detections:
        for color, (cx, cy), (x, y, w, h) in detections:
            color_bgr = (0, 0, 255) if color == "RED" else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color_bgr, 2)
            cv2.circle(frame, (cx, cy), 5, (255,255,255), -1)
            cv2.putText(frame, color, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_bgr, 2)

            if 220 < cx < 420:
                send_cmd("STOP")
                time.sleep(0.3)

                if color == "RED":
                    send_cmd("RIGHT")
                    action = "RIGHT"
                elif color == "GREEN":
                    send_cmd("LEFT")
                    action = "LEFT"

                # --- Turn and curve around the object ---
                time.sleep(1.2)   # turning time
                send_cmd("FWD")
                time.sleep(1.0)   # move forward slightly around obstacle
                send_cmd("LEFT" if color == "RED" else "RIGHT")  # curve back
                time.sleep(1.4)
                send_cmd("FWD")
                break
    else:
        send_cmd("FWD")

    cv2.putText(frame, f"Action: {action}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
    cv2.imshow("Traffic Box Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
