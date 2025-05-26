import cv2
from gpiozero import Servo
from time import sleep
import subprocess

# === Enable Autofocus (when supported) ===
def enable_autofocus():
    try:
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "-c", "focus_auto=1"], check=True)
        print("Autofocus enabled.")
    except Exception as e:
        print("Autofocus cannot be enabled:", e)

enable_autofocus()

# === Servo-configuration ===
pan_servo = Servo(17)
tilt_servo = Servo(18)

pan = 0.0
tilt = 0.0

def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))

def smooth_move(current, target, factor=0.02):
    return current + (target - current) * factor

# === Camera-settings ===
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

_, frame1 = cap.read()
gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)

# === movement constants ===
min_contour_area = 1500          # ignore small movements
min_offset_threshold = 0.10      # ignore small movements on screen

while True:
    _, frame2 = cap.read()
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

    diff = cv2.absdiff(gray1, gray2)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    motion_x = 0
    motion_y = 0

    for contour in contours:
        if cv2.contourArea(contour) < min_contour_area:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        motion_x = x + w // 2
        motion_y = y + h // 2
        motion_detected = True
        break  # Use first detected contour

    if motion_detected:
        frame_center_x = 640 // 2
        frame_center_y = 480 // 2
        offset_x = (motion_x - frame_center_x) / frame_center_x
        offset_y = (motion_y - frame_center_y) / frame_center_y

        # ignore small offsets
        if abs(offset_x) > min_offset_threshold or abs(offset_y) > min_offset_threshold:
            pan = smooth_move(pan, clamp(pan - offset_x * 0.5, -1, 1))
            tilt = smooth_move(tilt, clamp(tilt - offset_y * 0.5, -1, 1))

            pan_servo.value = pan
            tilt_servo.value = tilt

    # Update for the next iteration
    gray1 = gray2.copy()
    sleep(0.05)
