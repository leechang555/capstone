from car_control import assign_parking, print_parking_status, WHITE, BLUE, MARK
from datetime import datetime

def listen_for_car_color_data():
    # 현재 기능은 사용하지 않음
    pass

# 색상코드(문자열) → 차량 타입 매핑
color_to_type = {
    'WHITE': WHITE,   # 일반 차량
    'BLUE': BLUE,     # 전기 차량
    'MARK': MARK      # 장애인 차량 (초록색)
}

def handle_auto_entry(car_color):
    if car_color not in color_to_type:
        print("⚠️ 알 수 없는 차량 색상입니다.")
        return

    car_type = color_to_type[car_color]
    
    # 현재 시각 기록
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚗 [{now}] 차량 감지됨 - 유형: {car_type}")

    assign_parking(car_type)
    print_parking_status()
