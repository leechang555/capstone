from picamera2 import Picamera2
import time
import cv2

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

picam2.start()
time.sleep(2)

frame = picam2.capture_array()

# 이미지를 저장해서 확인
cv2.imwrite("capture_test.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
print("이미지 저장 완료: capture_test.jpg")
