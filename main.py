import cv2 as cv2
import RPi.GPIO as GPIO
import time

# Setup motor pins
LEFT_MOTOR = 17
RIGHT_MOTOR = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_MOTOR, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR, GPIO.OUT)

# Setup PWM
pwmL = GPIO.PWM(LEFT_MOTOR, 100)
pwmR = GPIO.PWM(RIGHT_MOTOR, 100)
pwmL.start(0)
pwmR.start(0)

# Capture from PiCam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    # Line detection
    M = cv2.moments(thresh)
    if M["m00"] > 0:
        cx = int(M["m10"]/M["m00"])  # ตำแหน่งเส้น
        error = cx - frame.shape[1]//2

        # PID (แบบง่าย: P only)
        Kp = 0.05
        turn = Kp * error

        left_speed = 50 - turn
        right_speed = 50 + turn

        pwmL.ChangeDutyCycle(max(0, min(100, left_speed)))
        pwmR.ChangeDutyCycle(max(0, min(100, right_speed)))

    cv2.imshow("Line", thresh)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
