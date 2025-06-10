import threading
import time
import torch
import easyocr
import cv2
import os
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2

from color_detector import detect_color
from carin import handle_auto_entry
import carout  # 출차 알고리즘

# YOLOv5 모델 로딩
model = torch.hub.load(
    'ultralytics/yolov5',
    'custom',
    path='lp_det.pt',
    force_reload=True
)

# OCR 한글 포함
reader = easyocr.Reader(['en', 'ko'])

# 저장 디렉토리 생성
Path("captures").mkdir(exist_ok=True)

# 최근 인식된 번호판 목록
processed_plates = set()
last_detect_time = 0


def license_plate_loop():
    global last_detect_time

    print("실시간 번호판 인식 시스템 시작")

    # 카메라 설정
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(2)

    while True:
        frame = picam2.capture_array()

        # YOLO로 번호판 탐지
        results = model(frame)

        for *box, conf, cls in results.xyxy[0]:
            x1, y1, x2, y2 = map(int, box)
            cropped = frame[y1:y2, x1:x2]

            # OCR 수행
            ocr_result = reader.readtext(cropped)
            if not ocr_result:
                continue

            sorted_result = sorted(ocr_result, key=lambda x: x[0][0][0])
            full_text = ''.join([text for _, text, score in sorted_result if score > 0.3])

            if len(full_text) < 5:
                print("⚠️ 글자 수 부족으로 번호판 무시됨")
                continue

            now = time.time()

            if full_text in processed_plates:
                print(f"⚠️ 이미 처리된 번호판입니다. ({full_text})")
                continue

            if now - last_detect_time < 5:
                print(f"⏳ 인식 대기 중... {int(5 - (now - last_detect_time))}초")
                continue

            # 색상 감지
            car_color = detect_color(cropped)
            print(f"🪪 번호판: {full_text}, 🎨 색상: {car_color}")

            # 이미지 저장
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captures/{now_str}_{full_text}_{car_color}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 저장 완료: {filename}")

            # 주차 자리 배정
            handle_auto_entry(car_color)

            # 기록
            processed_plates.add(full_text)
            last_detect_time = time.time()

        # 실시간 화면 표시
        cv2.imshow("번호판 인식 결과", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("'q' 키 입력으로 종료")
            break

    picam2.stop()
    cv2.destroyAllWindows()
    print("✅ 시스템 정상 종료")


def main():
    # 출차 알고리즘 병렬 실행
    t_out = threading.Thread(target=carout.sensor_loop, daemon=True)
    t_out.start()

    # 번호판 인식 루프 실행
    license_plate_loop()


if __name__ == "__main__":
    main()
