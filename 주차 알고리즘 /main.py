import threading
import cv2
from detector import LicensePlateDetector

import carin
import carout

def license_plate_loop():
    detector = LicensePlateDetector()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 카메라를 열 수 없습니다.", flush=True)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 프레임 읽기 실패", flush=True)
            break

        frame, texts = detector.detect_from_frame(frame)
        for text in texts:
            print(f"🪪 번호판 인식: {text}", flush=True)

        cv2.imshow("License Plate Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    t_in = threading.Thread(target=carin.listen_for_car_color_data, daemon=True)
    t_out = threading.Thread(target=carout.sensor_loop, daemon=True)

    t_in.start()
    t_out.start()

    license_plate_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n프로그램 종료 중...", flush=True)


# 📏 거리 측정 함수 (센서 하나에 대해 실행)
def measure_distance(trig, echo):
    GPIO.output(trig, True)
    time.sleep(0.00001)  # 10마이크로초 펄스
    GPIO.output(trig, False)

    start = time.time()
    timeout = start + 0.04  # 40ms 이상은 무시

    # ECHO 핀 LOW → HIGH 될 때까지 대기
    while GPIO.input(echo) == 0 and time.time() < timeout:
        start = time.time()

    # ECHO 핀 HIGH → LOW 될 때까지 대기
    while GPIO.input(echo) == 1 and time.time() < timeout:
        stop = time.time()

    elapsed = stop - start
    distance = elapsed * 34300 / 2  # 왕복 거리 → cm로 환산
    return distance

# 🔁 계속 반복하면서 주차 상태 확인
try:
    while True:
        print("\n📡 센서 거리 측정 중...")
        for zone in sensor_pins:
            for i, sensor in enumerate(sensor_pins[zone]):
                dist = measure_distance(sensor['TRIG'], sensor['ECHO'])
                # 25cm 이하일 경우 차량 있음(1), 아니면 없음(0)
                parking_zones[zone][i] = 1 if dist <= 25 else 0
            print(f"🅿️ {zone}: {parking_zones[zone]}")
        time.sleep(2)  # 2초마다 반복

except KeyboardInterrupt:
    print("\n🛑 프로그램 종료, GPIO 정리")
    GPIO.cleanup()
