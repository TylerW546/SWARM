from picamera2 import Picamera2
import cv2
import numpy as np
import time

IMAGE_WIDTH = 400
IMAGE_HEIGHT = 400

picam2 = Picamera2()
config = picam2.create_preview_configuration({"size": (IMAGE_WIDTH, IMAGE_HEIGHT), "format": "RGB888"})
picam2.configure(config)
picam2.set_controls({
    "AeEnable": False,  # Disable auto exposure
    "AwbEnable": False, # Disable auto white balance
})
picam2.start()
time.sleep(1)

# Create a window for sliders
cv2.namedWindow("Controls")

# Dummy callback (required)
def nothing(x):
    pass

# Create trackbars for lower + upper LAB
cv2.createTrackbar("L_min", "Controls", 53, 255, nothing)
cv2.createTrackbar("L_max", "Controls", 153, 255, nothing)

cv2.createTrackbar("A_min", "Controls", 80, 255, nothing)
cv2.createTrackbar("A_max", "Controls", 140, 255, nothing)

cv2.createTrackbar("B_min", "Controls", 67, 255, nothing)
cv2.createTrackbar("B_max", "Controls", 140, 255, nothing)

while True:
    frame = picam2.capture_array()
    frame = cv2.flip(frame, -1)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    R = frame_rgb[:, :, 0]
    G = frame_rgb[:, :, 1]
    B = frame_rgb[:, :, 2]

    r = 1
    # Create mask: red dominant pixels
    red_mask = ((R.astype(float) / (G + 1) > r) &
            (R.astype(float) / (B + 1) > r)).astype(np.uint8) * 255
    
    frame = cv2.GaussianBlur(frame, (5,5), 0)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    lab = cv2.bitwise_and(lab, lab, mask=red_mask)

    frame_rgb = cv2.bitwise_and(frame_rgb, frame_rgb, mask=red_mask)
    frame = cv2.bitwise_and(frame, frame, mask=red_mask)
    lab = cv2.bitwise_and(lab, lab, mask=red_mask)
    
    # all points for which red is greater than blue and green


    # Read slider values
    l_min = cv2.getTrackbarPos("L_min", "Controls")
    a_min = cv2.getTrackbarPos("A_min", "Controls")
    b_min = cv2.getTrackbarPos("B_min", "Controls")

    l_max = cv2.getTrackbarPos("L_max", "Controls")
    a_max = cv2.getTrackbarPos("A_max", "Controls")
    b_max = cv2.getTrackbarPos("B_max", "Controls")

    lower = np.array([l_min, a_min, b_min])
    upper = np.array([l_max, a_max, b_max])

    orange = cv2.inRange(lab, lower, upper)

    small_kernel = np.ones((3,3), np.uint8)
    kernel = np.ones((7,7), np.uint8)

    orange = cv2.morphologyEx(orange, cv2.MORPH_OPEN, small_kernel)
    orange = cv2.morphologyEx(orange, cv2.MORPH_DILATE, kernel)

    orange_circles = cv2.HoughCircles(
        orange, cv2.HOUGH_GRADIENT,
        dp=1, minDist=20,
        param1=50, param2=30,
        minRadius=5, maxRadius=1000
    )

    if orange_circles is not None:
        orange_circles = np.uint16(np.around(orange_circles))
        for i in orange_circles[0, :]:
            cv2.circle(frame_rgb, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv2.circle(frame_rgb, (i[0], i[1]), 2, (0, 0, 255), 3)
            break

    cv2.circle(lab, (IMAGE_WIDTH//2, IMAGE_HEIGHT//2), 10, (0, 0, 255), 2)

    cv2.imshow("lab", lab)
    cv2.imshow("frame_rgb", frame_rgb)
    cv2.imshow("orange", orange)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()