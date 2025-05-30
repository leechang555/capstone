import time
import RPi.GPIO as GPIO

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
white_toggle = True

# GPIO 초기 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for zone in sensor_pins:
    for sensor in sensor_pins[zone]:
        GPIO.setup(sensor['TRIG'], GPIO.OUT)
        GPIO.setup(sensor['ECHO'], GPIO.IN)
        GPIO.output(sensor['TRIG'], False)

time.sleep(2)

# 거리 측정
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
    return elapsed * 34300 / 2

# 빈 자리 찾기
def find_empty_spot(zone_name):
    for i in range(3):
        if parking_zones[zone_name][i] == 0:
            return i
    return None

# 입차 처리
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
        print(f"\n✅ 차량 종류: {car_type}")
        print(f"🅿️ '{assigned_zone}'의 {assigned_spot + 1}번 자리에 주차되었습니다.")
    else:
        print(f"\n❌ {car_type} 차량을 위한 빈 자리가 없습니다.")

# 센서로 주차 상태 갱신
def update_parking_from_sensor():
    for zone in sensor_pins:
        for i, sensor in enumerate(sensor_pins[zone]):
            dist = measure_distance(sensor['TRIG'], sensor['ECHO'])
            parking_zones[zone][i] = 1 if dist <= 25 else 0

# 상태 출력
def print_current_status():
    print("\n📊 실시간 주차 상태:")
    for zone, spots in parking_zones.items():
        print(f" - {zone}: {spots}")

# 메인 루프
try:
    while True:
        update_parking_from_sensor()
        print_current_status()

        # 사용자 입차 요청
        action = input("\n🚗 차량을 입차하시겠습니까? (예/아니오): ").strip()
        if action == '예':
            car_type = input("차량 종류를 입력하세요 (일반 차량 / 전기 차량 / 장애인 차량): ").strip()
            if car_type in [WHITE, BLUE, MARK]:
                assign_parking(car_type)
            else:
                print("⚠️ 올바른 차량 종류를 입력하세요.")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 종료: GPIO 정리")
    GPIO.cleanup()
