from picamera2 import Picamera2
import cv2
import numpy as np
import time

IMAGE_WIDTH = 400
IMAGE_HEIGHT = 400

picam2 = Picamera2()
config = picam2.create_preview_configuration({"size": (IMAGE_WIDTH, IMAGE_HEIGHT)})
picam2.configure(config)
picam2.set_controls({
    "AeEnable": False,  # Disable auto exposure
    "AwbEnable": False, # Disable auto white balance
})
picam2.start()
time.sleep(1)

while True:
    frame = picam2.capture_array()

    # Convert to HSV
    lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    cv2.circle(frame, center=(IMAGE_WIDTH//2, IMAGE_HEIGHT//2), radius=10, color=(0, 0, 255), thickness=2)
    print(frame[IMAGE_WIDTH//2][IMAGE_HEIGHT//2])

    # For tracking something bright orange
    lower = np.array([0, 164, 147])
    upper = np.array([255, 200, 200])

    mask = cv2.inRange(lab, lower, upper)

    cv2.circle(lab, center=(IMAGE_WIDTH//2, IMAGE_HEIGHT//2), radius=10, color=(0, 0, 255), thickness=2)

    # Find centroid
    moments = cv2.moments(mask)
    if moments["m00"] > 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        # print("Found at:", cx, cy)

        # draw for debugging
        cv2.circle(frame, center=(cx, cy), radius=100, color=(255, 0, 0), thickness=2)

    cv2.imshow("frame", frame)
    cv2.imshow("lab", lab)
    cv2.imshow("mask", mask)

    if cv2.waitKey(1) == 27:
        break
