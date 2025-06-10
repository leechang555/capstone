import RPi.GPIO as GPIO
import time
from car_control import parking_zones, remove_parking, print_parking_status

# 센서 핀 정의 (반드시 필요)
sensor_pins = {
    'T1A': [{'TRIG': 23, 'ECHO': 24}, {'TRIG': 3, 'ECHO': 14}],
    'T1B': [{'TRIG': 17, 'ECHO': 18}, {'TRIG': 12, 'ECHO': 13}],
    'T2A': [{'TRIG': 5, 'ECHO': 6}, {'TRIG': 9, 'ECHO': 10}],
    'T2B': [{'TRIG': 27,  'ECHO': 22}, {'TRIG': 20,  'ECHO': 21}],
    '전기차': [{'TRIG': 15, 'ECHO': 2}, {'TRIG': 0,  'ECHO': 1}],
    '장애인': [{'TRIG': 16, 'ECHO': 26}, {'TRIG': 11, 'ECHO': 25}]
}

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for zone in sensor_pins:
    for sensor in sensor_pins[zone]:
        GPIO.setup(sensor['TRIG'], GPIO.OUT)
        GPIO.setup(sensor['ECHO'], GPIO.IN)
        GPIO.output(sensor['TRIG'], False)

time.sleep(2)

# 거리 측정 함수
def measure_distance(trig, echo):
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    timeout = start_time + 0.04

    while GPIO.input(echo) == 0 and time.time() < timeout:
        start = time.time()

    while GPIO.input(echo) == 1 and time.time() < timeout:
        stop = time.time()

    elapsed = stop - start
    distance = elapsed * 34300 / 2
    return distance

# 출차 감지를 위한 거리 상태 저장
distance_counter = {
    zone: [0] * len(sensor_pins[zone]) for zone in sensor_pins
}

# 출차 감지 로직
def detect_and_handle_exit():
    for zone in sensor_pins:
        for idx, sensor in enumerate(sensor_pins[zone]):
            dist = measure_distance(sensor['TRIG'], sensor['ECHO'])
            current_state = parking_zones[zone][idx]

            if current_state == 1:
                if dist > 25:
                    distance_counter[zone][idx] += 1
                    if distance_counter[zone][idx] >= 3:
                        success = remove_parking(zone, idx + 1)
                        if success:
                            print(f"📢 출차 감지: '{zone}' {idx + 1}번 자리", flush=True)
                        distance_counter[zone][idx] = 0
                else:
                    distance_counter[zone][idx] = 0  # 가까워지면 리셋
            else:
                distance_counter[zone][idx] = 0  # 비어있을 때 초기화

    print_parking_status()

# 센서 감지 루프
def sensor_loop():
    try:
        while True:
            detect_and_handle_exit()
            time.sleep(2)  # 2초 주기
    except KeyboardInterrupt:
        print("\n⛔ 프로그램 수동 종료")
    finally:
        GPIO.cleanup()
