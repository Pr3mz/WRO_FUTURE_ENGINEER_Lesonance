import cv2, numpy as np, socket

ESP32_IP = "192.168.4.1"
ESP32_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(cmd: str):
    sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))

# Auto-detect camera
def find_camera(max_index=5):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            return cap
        cap.release()
    print("Error: No camera found")
    exit()

cap = find_camera()  # automatically finds first available camera

# HSV ranges for colors
ranges = {
    "RED1":  ((0, 120, 70),   (10, 255, 255)),
    "RED2":  ((170, 120, 70), (180, 255, 255)),
    "GREEN": ((40, 50, 50),   (85, 255, 255)),
    "BLUE":  ((100, 120, 50), (130, 255, 255)),
    "YELL":  ((20, 120, 120), (35, 255, 255))
}

def detect_color(hsv):
    masks = []
    red1 = cv2.inRange(hsv, *ranges["RED1"])
    red2 = cv2.inRange(hsv, *ranges["RED2"])
    red  = cv2.bitwise_or(red1, red2)
    masks.append(("RED", red))
    masks.append(("GREEN", cv2.inRange(hsv, *ranges["GREEN"])))
    masks.append(("BLUE",  cv2.inRange(hsv, *ranges["BLUE"])))
    masks.append(("YELL",  cv2.inRange(hsv, *ranges["YELL"])))

    winner, best_area = None, 0
    for name, m in masks:
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        area = max((cv2.contourArea(c) for c in cnts), default=0)
        if area > best_area:
            best_area, winner = area, name
    return (winner, best_area)

def obstacle_in_center(gray):
    h, w = gray.shape
    roi = gray[int(h*0.45):int(h*0.85), int(w*0.35):int(w*0.65)]
    _, th = cv2.threshold(roi, 60, 255, cv2.THRESH_BINARY_INV)
    area = cv2.countNonZero(th)
    return area > (roi.size * 0.18)

while True:
    ok, frame = cap.read()
    if not ok: break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    color, area = detect_color(hsv)
    has_obstacle = obstacle_in_center(gray)

    if has_obstacle:
        send("STOP")
        status = "Obstacle→STOP"
    else:
        if   color == "RED"  and area > 1500:  send("BACK");  status = "RED→BACK"
        elif color == "GREEN" and area > 1500: send("FWD");   status = "GREEN→FWD"
        elif color == "BLUE" and area > 1500:  send("LEFT");  status = "BLUE→LEFT"
        elif color == "YELL" and area > 1500:  send("RIGHT"); status = "YELL→RIGHT"
        else:
            send("STOP"); status = "No big color→STOP"

    cv2.putText(frame, status, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow("AI Vision", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
