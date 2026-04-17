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
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    blurframe = cv2.GaussianBlur(frame, (5,5), 0)
    lab = cv2.cvtColor(blurframe, cv2.COLOR_BGR2LAB)

    lower = np.array([120, 100, 120])
    upper = np.array([255, 160, 230])

    print("Color at image center: ", lab[IMAGE_HEIGHT//2, IMAGE_WIDTH//2])
    cv2.circle(lab, center=(IMAGE_WIDTH//2, IMAGE_HEIGHT//2), radius=10, color=(0, 0, 255), thickness=2)
    

    mask = cv2.inRange(lab, lower, upper)

    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    pixel_count = cv2.countNonZero(mask)

    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=5, maxRadius=1000)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
            break

    cv2.imshow("lab", lab)
    cv2.imshow("frame", frame)
    cv2.imshow("blur", blurframe)
    cv2.imshow("mask", mask)

    if cv2.waitKey(1) == 27:
        break
