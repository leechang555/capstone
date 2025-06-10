from picamera2 import Picamera2
import time
import cv2
import easyocr
import matplotlib.pyplot as plt

# OCR 엔진 초기화
reader = easyocr.Reader(['en'])  # 한글까지 필요하면 ['en', 'ko']

# 카메라 설정
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(2)

# 프레임 1장 캡처
frame = picam2.capture_array()

# OCR 수행
results = reader.readtext(frame)

# 결과 출력
for bbox, text, conf in results:
    print(f"📌 인식된 텍스트: {text} (정확도: {conf:.2f})")

# 이미지 출력
for bbox, text, conf in results:
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(frame, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

cv2.imshow("OCR Result", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
picam2.stop()
