# 차량 종류 상수
WHITE = '일반 차량'
BLUE = '전기 차량'
MARK = '장애인 차량'

# 각 구역별 자리 수 (2자리로 통일)
zones = ['T1A', 'T1B', 'T2A', 'T2B', '전기차', '장애인']

# 주차 상태 초기화: 0=빈자리, 1=차 있음
parking_zones = {zone: [0, 0] for zone in zones}

white_toggle = True  # 일반 차량 입차 시 T1A, T1B 번갈아 배정용

def find_empty_spot(zone_name):
    for i, status in enumerate(parking_zones[zone_name]):
        if status == 0:
            return i
    return None

def assign_parking(car_type):
    global white_toggle
    assigned = False
    assigned_zone = None
    assigned_spot = None

    if car_type == WHITE:
        preferred_order = ['T1A', 'T1B', 'T2A', 'T2B']
        # T1A, T1B 번갈아 배정
        if white_toggle:
            preferred_order = ['T1A', 'T1B', 'T2A', 'T2B']
        else:
            preferred_order = ['T1B', 'T1A', 'T2A', 'T2B']
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
        print(f"{zone}: {' '.join(status)}", flush=True)
