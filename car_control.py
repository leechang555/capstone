# ✅ 수정된 car_control.py 전체 코드

import RPi.GPIO as GPIO
import time

# 차량 종류 상수
WHITE = '일반 차량'
BLUE = '전기 차량'
MARK = '장애인 차량'

# 각 구역별 자리 수
zones = ['T1A', 'T1B', 'T2A', 'T2B', '전기차', '장애인']
parking_zones = {zone: [0, 0] for zone in zones}

# 센서 핀 매핑
sensor_pins = {
    'T1A': [{'TRIG': 23, 'ECHO': 24}, {'TRIG': 3, 'ECHO': 14}],
    'T1B': [{'TRIG': 17, 'ECHO': 18}, {'TRIG': 12, 'ECHO': 13}],
    'T2A': [{'TRIG': 5, 'ECHO': 6}, {'TRIG': 9, 'ECHO': 10}],
    'T2B': [{'TRIG': 27,  'ECHO': 22}, {'TRIG': 20,  'ECHO': 21}],
    '전기차': [{'TRIG': 15, 'ECHO': 2}, {'TRIG': 0,  'ECHO': 1}],
    '장애인': [{'TRIG': 16, 'ECHO': 26}, {'TRIG': 11, 'ECHO': 25}]
}

# ✅ GPIO 초기화 (이 코드는 항상 실행되어야 함)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for zone in sensor_pins:
    for sensor in sensor_pins[zone]:
        GPIO.setup(sensor['TRIG'], GPIO.OUT)
        GPIO.setup(sensor['ECHO'], GPIO.IN)
        GPIO.output(sensor['TRIG'], False)

white_toggle = True

def find_empty_spot(zone_name):
    for i, status in enumerate(parking_zones[zone_name]):
        if status == 0:
            return i
    return None

# ✅ 거리 측정 함수
# (혹시 GPIO 초기화 누락되었을 경우 대비 안전 장치 포함)
def measure_distance(trig, echo):
    try:
        # 🔒 안정성을 위한 안전 재설정
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)
    except RuntimeError as e:
        print(f"⚠️ GPIO 오류 발생: {e}")
        return 999  # 오류 시 임시 반환값

    start_time = time.time()
    timeout = start_time + 0.04

    while GPIO.input(echo) == 0 and time.time() < timeout:
        start = time.time()

    while GPIO.input(echo) == 1 and time.time() < timeout:
        stop = time.time()

    elapsed = stop - start
    distance = elapsed * 34300 / 2
    return distance


# ⏳ 입차 후 센서 거리 확인 함수

def activate_sensor_after_delay(zone, idx):
    print(f"⏳ 입차 후 5초 대기 중... ({zone} {idx+1}번 자리)")
    time.sleep(5)
    sensor = sensor_pins[zone][idx]
    dist = measure_distance(sensor['TRIG'], sensor['ECHO'])
    if dist <= 25:
        print(f"✅ 센서 확인 완료: 차량 있음 ({dist:.1f}cm)")
    else:
        print(f"⚠️ 센서 확인 실패: 차량 없음 ({dist:.1f}cm)")

# 🚗 차량 입차 자리 배정 함수

def assign_parking(car_type):
    global white_toggle
    assigned = False
    assigned_zone = None
    assigned_spot = None

    if car_type == WHITE:
        preferred_order = ['T1A', 'T1B', 'T2A', 'T2B'] if white_toggle else ['T1B', 'T1A', 'T2B', 'T2A']
        white_toggle = not white_toggle
        for zone in preferred_order:
            spot = find_empty_spot(zone)
            if spot is not None:
                parking_zones[zone][spot] = 1
                assigned_zone = zone
                assigned_spot = spot
                assigned = True
                break

    elif car_type == BLUE:
        for zone in ['전기차']:
            spot = find_empty_spot(zone)
            if spot is not None:
                parking_zones[zone][spot] = 1
                assigned_zone = zone
                assigned_spot = spot
                assigned = True
                break

    elif car_type == MARK:
        for zone in ['장애인']:
            spot = find_empty_spot(zone)
            if spot is not None:
                parking_zones[zone][spot] = 1
                assigned_zone = zone
                assigned_spot = spot
                assigned = True
                break

    if assigned:
        print(f"✅ 차량 종류: {car_type}", flush=True)
        print(f"🅿️ '{assigned_zone}' 구역 {assigned_spot + 1}번 자리에 주차되었습니다.", flush=True)
        activate_sensor_after_delay(assigned_zone, assigned_spot)
    else:
        print(f"❌ {car_type}을(를) 위한 주차 공간이 모두 찼습니다.", flush=True)

    return assigned_zone, assigned_spot

def remove_parking(zone_name, spot_number):
    if zone_name not in parking_zones:
        print(f"❌ '{zone_name}' 구역이 존재하지 않습니다.", flush=True)
        return False

    spot_index = spot_number - 1
    if spot_index < 0 or spot_index >= len(parking_zones[zone_name]):
        print(f"❌ 자리 번호가 올바르지 않습니다.", flush=True)
        return False

    if parking_zones[zone_name][spot_index] == 0:
        print(f"❌ 해당 자리({spot_number}번)는 이미 비어 있습니다.", flush=True)
        return False
    else:
        parking_zones[zone_name][spot_index] = 0
        print(f"✅ '{zone_name}' 구역 {spot_number}번 자리 차량이 출차되었습니다.", flush=True)
        return True

def print_parking_status():
    print("\n[현재 주차 현황]", flush=True)
    for zone in parking_zones:
        status = ["○" if s == 0 else "●" for s in parking_zones[zone]]
        total = len(parking_zones[zone])
        occupied = sum(parking_zones[zone])
        print(f"{zone}: {' '.join(status)}  ▶️ 주차 현황: ({occupied}/{total})", flush=True)
