from picamera2 import Picamera2
import time
import cv2
import torch
import easyocr
import os
from color_detector import detect_color  # 색상 감지 모듈 임포트

# YOLOv5 모델 로딩 (번호판 검출용)
model = torch.hub.load(
    'ultralytics/yolov5',
    'custom',
    path='lp_det.pt',
    force_reload=True
)

# OCR 리더 (한글 포함)
reader = easyocr.Reader(['en', 'ko'])

# 카메라 초기화
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(2)

print("\U0001F4F8 2초 간격으로 2장 촬영 시작")

# 저장 디렉토리 생성
os.makedirs("captures", exist_ok=True)

for i in range(2):
    print(f"\n\U0001F4F7 {i+1}/2번째 촬영 중...")

    frame = picam2.capture_array()

    # YOLO로 번호판 탐지
    results = model(frame)
    print(f"\U0001F50D YOLO 탐지 수: {len(results.xyxy[0])}")

    for *box, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        cropped = frame[y1:y2, x1:x2]

        # OCR 수행
        ocr_result = reader.readtext(cropped)

        if ocr_result:
            # 인식 결과 왼쪽 기준 정렬
            results_sorted = sorted(ocr_result, key=lambda x: x[0][0][0])
            full_text = ''.join([text for _, text, score in results_sorted if score > 0.3])
            print(f"\U0001F4DB 번호판 텍스트: {full_text}")

            # 색상 분류
            color_label = detect_color(cropped)
            print(f"🎨 번호판 배경색: {color_label}")

            # 시각화
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{full_text} ({color_label})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            print("❌ 번호판 인식 실패")

    # 이미지 저장
    image_path = f"captures/capture_{i+1}.jpg"
    cv2.imwrite(image_path, frame)
    print(f"\U0001F4BE 이미지 저장 완료: {image_path}")

    cv2.imshow("번호판 인식 결과", frame)
    cv2.waitKey(1000)
    time.sleep(2)

picam2.stop()
cv2.destroyAllWindows()
print("✅ 촬영 및 저장 완료")
