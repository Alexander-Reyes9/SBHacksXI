import cv2
import numpy as np
import threading

normalized_movement = 0.0

def detect_movement():
    global normalized_movement

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot access video source")
        return

    previous_frame = None
    max_movement_value = 1920 * 1080  # Update based on your frame resolution
    max_movement_percent = max_movement_value / 3  # Assume a third of the max white pixels

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video stream or cannot fetch the frame.")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (7, 7), 0)  # Reduce noise

        if previous_frame is not None:
            frame_diff = cv2.absdiff(previous_frame, gray_frame)
            _, threshold = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
            movement_area = np.sum(threshold > 0)
            normalized_movement = movement_area / max_movement_value

        previous_frame = gray_frame
        cv2.waitKey(1)

# Run movement detection in a separate thread
movement_thread = threading.Thread(target=detect_movement)
movement_thread.daemon = True
movement_thread.start()
