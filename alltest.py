import threading
import time
import torch
import easyocr
import cv2
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2

from color_detector import detect_color
from carin import handle_auto_entry
import carout  # 출차 감지

# YOLOv5 번호판 모델 로딩
model = torch.hub.load(
    'ultralytics/yolov5',
    'custom',
    path='lp_det.pt',
    force_reload=True
)

reader = easyocr.Reader(['en', 'ko'])  # 한글 포함 OCR 리더
Path("captures").mkdir(exist_ok=True)  # 이미지 저장 폴더 생성

processed_plates = set()  # 중복 번호판 방지용
last_detect_time = 0


def limited_license_plate_loop():
    global last_detect_time
    print("🎬 번호판 인식 시작 (4회 제한)")

    # 카메라 초기화
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(2)

    capture_count = 0
    while capture_count < 4:
        frame = picam2.capture_array()

        # YOLO 탐지
        results = model(frame)

        for *box, conf, cls in results.xyxy[0]:
            x1, y1, x2, y2 = map(int, box)
            cropped = frame[y1:y2, x1:x2]

            # OCR
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

            # 색상 인식
            car_color = detect_color(cropped)
            print(f"🪪 번호판: {full_text}, 🎨 색상: {car_color}")

            # 저장
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captures/{now_str}_{full_text}_{car_color}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 저장 완료: {filename}")

            # 주차 배정
            handle_auto_entry(car_color)

            processed_plates.add(full_text)
            last_detect_time = now

        capture_count += 1
        print(f"📸 캡처 {capture_count}/4회 완료\n")
        time.sleep(2)

        cv2.imshow("번호판 인식 결과", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 'q' 입력으로 조기 종료")
            break

    picam2.stop()
    cv2.destroyAllWindows()
    print("✅ 4회 인식 종료, 프로그램 대기 중 (q를 누르면 종료됨)")

    # 이후 화면 유지 (사용자 q 누를 때까지)
    while True:
        key = cv2.waitKey(100)
        if key == ord('q'):
            print("🛑 프로그램 종료")
            break


def main():
    # 출차 감지 쓰레드 실행
    t_out = threading.Thread(target=carout.sensor_loop, daemon=True)
    t_out.start()

    # 입차 감지 (4회 제한)
    limited_license_plate_loop()


if __name__ == "__main__":
    main()
