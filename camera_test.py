from picamera2 import Picamera2
import time
import cv2
import matplotlib.pyplot as plt

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

picam2.start()
time.sleep(2)

frame = picam2.capture_array()

plt.imshow(frame)
plt.axis('off')
plt.title("Captured Image")
plt.show()