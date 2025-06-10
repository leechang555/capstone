import threading
import time
import cv2
import torch
import easyocr
import os
from picamera2 import Picamera2
from color_detector import detect_color
import carin

# YOLO 모델 로드
model = torch.hub.load(
    'ultralytics/yolov5',
    'custom',
    path='lp_det.pt',
    force_reload=True
)

# EasyOCR 초기화
reader = easyocr.Reader(['en', 'ko'])

# 캡처 저장 디렉토리 생성
os.makedirs("captures", exist_ok=True)

# 중복 방지를 위한 최근 인식 번호판 리스트
recognized_plates = []
MAX_HISTORY = 10

def is_duplicate(plate_text):
    return plate_text in recognized_plates

def add_to_history(plate_text):
    recognized_plates.append(plate_text)
    if len(recognized_plates) > MAX_HISTORY:
        recognized_plates.pop(0)

def license_plate_loop():
    print("📸 실시간 번호판 인식 시작")
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(2)

    last_detection_time = 0  # 마지막 인식 시간

    while True:
        frame = picam2.capture_array()
        current_time = time.time()

        if current_time - last_detection_time >= 5:
            results = model(frame)

            for *box, conf, cls in results.xyxy[0]:
                x1, y1, x2, y2 = map(int, box)
                cropped = frame[y1:y2, x1:x2]

                ocr_result = reader.readtext(cropped)
                if ocr_result:
                    sorted_result = sorted(ocr_result, key=lambda x: x[0][0][0])
                    full_text = ''.join([text for _, text, score in sorted_result if score > 0.3])

                    if len(full_text) < 5:
                        print("❌ 글자 수 부족 - 인식 무시")
                        continue

                    if is_duplicate(full_text):
                        print(f"🔁 중복 인식된 번호판: {full_text} - 무시")
                        continue

                    print(f"🪪 인식된 번호판: {full_text}")
                    add_to_history(full_text)

                    color_label = detect_color(cropped)
                    print(f"🎨 인식된 차량 색상: {color_label}")

                    carin.handle_auto_entry(color_label)

                    image_path = f"captures/{full_text}_{int(time.time())}.jpg"
                    cv2.imwrite(image_path, frame)
                    print(f"💾 이미지 저장 완료: {image_path}")

                    last_detection_time = current_time
                    break  # 한 번 인식했으면 다음 프레임으로

        # 화면에 출력
        cv2.imshow("실시간 번호판 인식", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()
    print("🛑 번호판 인식 종료됨")

def main():
    t_in = threading.Thread(target=carin.listen_for_car_color_data, daemon=True)
    t_in.start()
    license_plate_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 수동 종료됨")
