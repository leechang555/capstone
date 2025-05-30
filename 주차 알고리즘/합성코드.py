import RPi.GPIO as GPIO
import time

# 차량 종류 상수
WHITE = '일반 차량'
BLUE = '전기 차량'
MARK = '장애인 차량'

# 센서 핀 설정
sensor_pins = {
    'T1A': [{'TRIG': 23, 'ECHO': 24}, {'TRIG': 27, 'ECHO': 22}, {'TRIG': 5,  'ECHO': 6}],
    'T1B': [{'TRIG': 17, 'ECHO': 18}, {'TRIG': 12, 'ECHO': 16}, {'TRIG': 20, 'ECHO': 21}],
    'T2A': [{'TRIG': 13, 'ECHO': 19}, {'TRIG': 26, 'ECHO': 4},  {'TRIG': 25, 'ECHO': 8}],
    'T2B': [{'TRIG': 7,  'ECHO': 1},  {'TRIG': 9,  'ECHO': 10}, {'TRIG': 11, 'ECHO': 14}],
    '전기차': [{'TRIG': 15, 'ECHO': 2}, {'TRIG': 3,  'ECHO': 28}, {'TRIG': 29, 'ECHO': 30}],
    '장애인': [{'TRIG': 31, 'ECHO': 32}, {'TRIG': 33, 'ECHO': 34}, {'TRIG': 35, 'ECHO': 36}]
}

# 주차 상태 초기화
parking_zones = {zone: [0, 0, 0] for zone in sensor_pins}

# GPIO 세팅
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for zone in sensor_pins:
    for sensor in sensor_pins[zone]:
        GPIO.setup(sensor['TRIG'], GPIO.OUT)
        GPIO.setup(sensor['ECHO'], GPIO.IN)
        GPIO.output(sensor['TRIG'], False)

time.sleep(2)  # 센서 안정화

def measure_distance(trig, echo):
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start = time.time()
    timeout = start + 0.04

    while GPIO.input(echo) == 0 and time.time() < timeout:
        start = time.time()

    while GPIO.input(echo) == 1 and time.time() < timeout:
        stop = time.time()

    elapsed = stop - start
    distance = elapsed * 34300 / 2
    return distance

def find_empty_spot(zone_name):
    for i in range(3):
        if parking_zones[zone_name][i] == 0:
            return i
    return None

white_toggle = True

def assign_parking(car_type):
    global white_toggle
    assigned = False
    assigned_zone = None
    assigned_spot = None

    if car_type == WHITE:
        preferred_order = ['T1A', 'T1B'] if white_toggle else ['T1B', 'T1A']
        white_toggle = not white_toggle
        for zone in preferred_order + ['T2A', 'T2B']:
            spot = find_empty_spot(zone)
            if spot is not None:
                parking_zones[zone][spot] = 1
                assigned_zone = zone
                assigned_spot = spot
                assigned = True
                break

    elif car_type == BLUE:
        spot = find_empty_spot('전기차')
        if spot is not None:
            parking_zones['전기차'][spot] = 1
            assigned_zone = '전기차'
            assigned_spot = spot
            assigned = True

    elif car_type == MARK:
        spot = find_empty_spot('장애인')
        if spot is not None:
            parking_zones['장애인'][spot] = 1
            assigned_zone = '장애인'
            assigned_spot = spot
            assigned = True

    if assigned:
        print(f"✅ 차량 종류: {car_type}")
        print(f"🅿️ '{assigned_zone}' 구역 {assigned_spot + 1}번 자리에 주차되었습니다.")
        current_status = parking_zones[assigned_zone]
        empty_count = current_status.count(0)
        print(f"📊 현재 '{assigned_zone}' 주차 현황: {empty_count}/3 자리 비어 있음 -> {current_status}\n")
    else:
        print(f"❌ {car_type}을(를) 위한 주차 공간이 모두 찼습니다.\n")

def remove_parking(zone_name, spot_number):
    if zone_name not in parking_zones:
        print(f"❌ '{zone_name}' 구역이 존재하지 않습니다.\n")
        return
    
    spot_index = spot_number - 1
    if spot_index < 0 or spot_index >= len(parking_zones[zone_name]):
        print(f"❌ 자리 번호가 올바르지 않습니다. 1 ~ {len(parking_zones[zone_name])} 사이여야 합니다.\n")
        return
    
    if parking_zones[zone_name][spot_index] == 0:
        print(f"❌ 해당 자리({spot_number}번)는 이미 비어 있습니다.\n")
    else:
        parking_zones[zone_name][spot_index] = 0
        print(f"✅ '{zone_name}' 구역 {spot_number}번 자리 차량이 출차되었습니다.")
        current_status = parking_zones[zone_name]
        empty_count = current_status.count(0)
        print(f"📊 '{zone_name}' 주차 현황: {empty_count}/3 자리 비어 있음 -> {current_status}\n")

def print_parking_status():
    print("\n📡 센서 거리 측정 중...")
    for zone in sensor_pins:
        empty_count = parking_zones[zone].count(0)
        print(f"🅿️ {zone}: {parking_zones[zone]} (빈 자리 {empty_count}/3)")
    print()  # 한 줄 띄움

try:
    while True:
        # 센서로 거리 측정 및 주차 상태 갱신
        for zone in sensor_pins:
            for i, sensor in enumerate(sensor_pins[zone]):
                dist = measure_distance(sensor['TRIG'], sensor['ECHO'])
                parking_zones[zone][i] = 1 if dist <= 25 else 0
        print_parking_status()

        action = input("🚦 입차 또는 종료를 입력하세요: ").strip()
        if action == "종료":
            break
        elif action == "입차":
            car_type = input("차량 종류를 입력하세요 (일반 차량 / 전기 차량 / 장애인 차량): ").strip()
            if car_type not in [WHITE, BLUE, MARK]:
                print("⚠️ 올바른 차량 종류를 입력하세요.\n")
            else:
                assign_parking(car_type)
        else:
            print("⚠️ '입차' 또는 '종료' 중 하나를 입력하세요.\n")

except KeyboardInterrupt:
    print("\n🛑 프로그램 종료, GPIO 정리 중...")

finally:
    GPIO.cleanup()
