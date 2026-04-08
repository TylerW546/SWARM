from picamera2 import Picamera2
import cv2
import numpy as np
import time

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(1)

while True:
    frame = picam2.capture_array()

    # Convert to HSV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # For tracking something bright orange
    lower = np.array([104, 150, 50])
    upper = np.array([120, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    h, w, _ = frame.shape
    print(hsv[h//2, w//2])

    # Find centroid
    moments = cv2.moments(mask)
    if moments["m00"] > 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        # print("Found at:", cx, cy)

        # draw for debugging
        cv2.circle(frame, center=(cx, cy), radius=100, color=(255, 0, 0), thickness=2)

    cv2.imshow("frame", frame)
    cv2.imshow("mask", mask)

    if cv2.waitKey(1) == 27:
        break
