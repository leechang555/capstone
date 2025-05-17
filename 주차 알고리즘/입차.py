# 차량 종류 상수
WHITE = '일반 차량'
BLUE = '전기 차량'
MARK = '장애인 차량'

# 초기 주차 구역 상태
initial_parking_zones = {
    'T1A': [0, 0, 0],
    'T1B': [0, 0, 0],
    'T2A': [0, 0, 0],
    'T2B': [0, 0, 0],
    '전기차': [0, 0, 0],
    '장애인': [0, 0, 0]
}

# 현재 주차 상태
parking_zones = initial_parking_zones.copy()

# 일반 차량 토글 (T1A ↔ T1B 순서 전환용)
white_toggle = True

def find_empty_spot(zone_name):
    for i in range(3):
        if parking_zones[zone_name][i] == 0:
            return i
    return None

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
        print(f"🅿️  '{assigned_zone}'의 {assigned_spot + 1}번 자리에 주차되었습니다.")
        current_status = parking_zones[assigned_zone]
        print(f"📊 현재 '{assigned_zone}' 주차 현황: {current_status.count(0)}/3 자리 비어 있음 -> {current_status}\n")
    else:
        print(f"\n❌ {car_type}을(를) 위한 주차 공간이 모두 찼습니다.\n")

def remove_parking(zone_name, spot_number):
    if zone_name not in parking_zones:
        print(f"❌ '{zone_name}' 구역이 존재하지 않습니다.")
        return
    
    spot_index = spot_number - 1
    if spot_index < 0 or spot_index >= len(parking_zones[zone_name]):
        print(f"❌ 자리 번호가 올바르지 않습니다. 1 ~ {len(parking_zones[zone_name])} 사이여야 합니다.")
        return
    
    if parking_zones[zone_name][spot_index] == 0:
        print(f"❌ 해당 자리({spot_number}번)는 이미 비어 있습니다.")
    else:
        parking_zones[zone_name][spot_index] = 0
        print(f"\n✅ '{zone_name}' 구역 {spot_number}번 자리 차량이 출차되었습니다.")
        current_status = parking_zones[zone_name]
        empty_count = current_status.count(0)
        print(f"📊 '{zone_name}' 주차 현황: {empty_count}/3 자리 비어 있음 -> {current_status}\n")

def print_current_occupancy():
    print("\n📌 현재 주차 현황:")
    for zone, spots in parking_zones.items():
        print(f" - {zone}: {spots}")
    print()

while True:
    print("🚦 입차, 출차 또는 종료를 선택하세요.")
    action = input("입차 / 출차 / 종료: ").strip()

    if action == "종료":
        break
    elif action == "입차":
        car_type = input("차량 종류를 입력하세요 (일반 차량 / 전기 차량 / 장애인 차량): ").strip()
        if car_type not in [WHITE, BLUE, MARK]:
            print("⚠️ 올바른 차량 종류를 입력하세요.\n")
        else:
            assign_parking(car_type)
    elif action == "출차":
        print_current_occupancy()
        inp = input("출차할 구역 및 자리 번호를 입력하세요 : ").strip()
        if '-' not in inp:
            print("⚠️ 입력 형식이 올바르지 않습니다.\n")
            continue
        zone_name, spot_str = inp.split('-', 1)
        zone_name = zone_name.strip()
        spot_str = spot_str.strip()
        if not spot_str.isdigit():
            print("⚠️ 자리 번호는 숫자여야 합니다.\n")
            continue
        spot_number = int(spot_str)
        remove_parking(zone_name, spot_number)
    else:
        print("⚠️ '입차', '출차', '종료' 중 하나를 입력하세요.\n")
