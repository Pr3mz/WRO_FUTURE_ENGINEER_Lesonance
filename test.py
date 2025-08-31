import cv2, numpy as np, socket, time, math

ESP32_IP = "192.168.4.1"
ESP32_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_cmd(cmd: str):
    sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))

# --- Camera auto-find ---
def find_camera(max_index=6):
    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            return cap
        cap.release()
    print("Error: No camera found")
    exit()

cap = find_camera()

# --- HSV ranges ---
ranges = {
    "RED1": ((0, 100, 60), (10, 255, 255)),
    "RED2": ((170, 100, 60), (180, 255, 255)),
    "GREEN": ((35, 60, 40), (85, 255, 255)),
    "BLUE": ((95, 80, 50), (130, 255, 255)),
    "YELLOW": ((18, 100, 100), (35, 255, 255)),
    "PURPLE": ((125, 50, 50), (155, 255, 255))
}

KERNEL = np.ones((5,5), np.uint8)

def clean_mask(mask):
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=1)
    return mask

def detect_color_and_shape(hsv):
    masks = {}
    # Red has two ranges
    r1 = cv2.inRange(hsv, *ranges["RED1"])
    r2 = cv2.inRange(hsv, *ranges["RED2"])
    masks["RED"] = clean_mask(cv2.bitwise_or(r1, r2))
    masks["GREEN"] = clean_mask(cv2.inRange(hsv, *ranges["GREEN"]))
    masks["BLUE"] = clean_mask(cv2.inRange(hsv, *ranges["BLUE"]))
    masks["YELLOW"] = clean_mask(cv2.inRange(hsv, *ranges["YELLOW"]))
    masks["PURPLE"] = clean_mask(cv2.inRange(hsv, *ranges["PURPLE"]))

    best = {"name": None, "area": 0, "centroid": None, "circ": 0, "bbox": None, "approx": None}

    for color, mask in masks.items():
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        # pick largest contour
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area < 200:
            continue
        peri = cv2.arcLength(c, True)
        circ = 4 * math.pi * area / (peri * peri) if peri > 0 else 0
        M = cv2.moments(c)
        cx = int(M["m10"] / M["m00"]) if M["m00"] else None
        cy = int(M["m01"] / M["m00"]) if M["m00"] else None
        x, y, w, h = cv2.boundingRect(c)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)  # polygon approximation

        if area > best["area"]:
            best.update({
                "name": color,
                "area": area,
                "centroid": (cx, cy),
                "circ": circ,
                "bbox": (x, y, w, h),
                "approx": approx
            })
    return best, masks

# --- lap tracking ---
lap_count = 0
lap_colors_seen = set()
state = "path"

# --- Main loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (640, 480))
    blurred = cv2.GaussianBlur(frame, (5,5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    best, masks = detect_color_and_shape(hsv)
    cxcy = best["centroid"]
    color = best["name"]
    area = best["area"]
    circ = best["circ"]
    bbox = best["bbox"]
    approx = best["approx"]

    # --- Lap detection ---
    if color in ("RED","YELLOW","BLUE"):
        lap_colors_seen.add(color)
    if len(lap_colors_seen) == 3:
        lap_count += 1
        lap_colors_seen.clear()
        print(f"Lap {lap_count} completed")

    # --- Traffic light cylinder detection ---
    cylinder_ahead = False
    if color in ("RED","GREEN") and area > 2000 and circ > 0.45:
        cylinder_ahead = True
        if cxcy and 0.35*frame.shape[1] < cxcy[0] < 0.65*frame.shape[1]:
            if color == "RED":
                send_cmd("LEFT")
            elif color == "GREEN":
                send_cmd("RIGHT")
            continue

    # --- Path movement ---
    if state == "path":
        send_cmd("FWD")

    # --- Purple wall parking after 3 laps ---
    if lap_count >= 3 and color == "PURPLE" and area > 3000:
        x, y, w, h = bbox
        if w >= frame.shape[1]*0.55:
            send_cmd("FWD")
            time.sleep(2)
            send_cmd("STOP")
            print("Reached purple wall, parked!")
            break

    # --- Debug overlay ---
    if cxcy:
        cv2.circle(frame, cxcy, 6, (0,255,0), -1)
    if bbox:
        x, y, w, h = bbox
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,255), 2)
    if approx is not None:
        cv2.drawContours(frame, [approx], -1, (0,255,255), 2)

    status = f"Color:{color} Lap:{lap_count} Area:{int(area)} Circ:{circ:.2f}"
    cv2.putText(frame, status, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("AI Vision", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
