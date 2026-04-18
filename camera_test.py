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
    frame = cv2.flip(frame, 0)

    frame = cv2.GaussianBlur(frame, (5,5), 0)
    lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)

    

    print("Color at image center: ", lab[IMAGE_HEIGHT//2, IMAGE_WIDTH//2])

    # orange
    lower = np.array([60, 110, 140])
    upper = np.array([255, 180, 230])
    orange = cv2.inRange(lab, lower, upper)

    # # blue
    # lower = np.array([100, 100, 100])
    # upper = np.array([255, 180, 230])
    # blue = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_RGB2HSV), lower, upper)
    

    small_kernel = np.ones((5,5), np.uint8)
    kernel = np.ones((7,7), np.uint8)
    orange = cv2.morphologyEx(orange, cv2.MORPH_OPEN, small_kernel)
    orange = cv2.morphologyEx(orange, cv2.MORPH_DILATE, kernel)
    
    # blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, small_kernel)
    # blue = cv2.morphologyEx(blue, cv2.MORPH_DILATE, kernel)
    

    orange_circles = cv2.HoughCircles(orange, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=5, maxRadius=1000)
    # blue_circles = cv2.HoughCircles(blue, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=5, maxRadius=1000)
    if orange_circles is not None:
        orange_circles = np.uint16(np.around(orange_circles))
        for i in orange_circles[0, :]:
            # draw the outer circle
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
            break

    cv2.circle(lab, center=(IMAGE_WIDTH//2, IMAGE_HEIGHT//2), radius=10, color=(0, 0, 255), thickness=2)
    

    cv2.imshow("lab", lab)
    cv2.imshow("frame", frame)
    cv2.imshow("orange", orange)

    if cv2.waitKey(1) == 27:
        break
