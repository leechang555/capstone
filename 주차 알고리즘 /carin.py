from car_control import assign_parking, print_parking_status, WHITE, BLUE, MARK

def handle_auto_entry(car_type):
    if car_type not in [WHITE, BLUE, MARK]:
        print("⚠️ 올바른 차량 종류가 아닙니다.", flush=True)
        return
    assign_parking(car_type)
    print_parking_status()

def receive_car_type():
    # 실제 센서 또는 카메라 데이터 수신 구현 예정
    # 임시로 무한루프에서 None 반환
    return None

def listen_for_car_color_data():
    while True:
        car_type = receive_car_type()
        if car_type:
            handle_auto_entry(car_type)

