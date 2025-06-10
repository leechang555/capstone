from car_control import assign_parking, print_parking_status, WHITE, BLUE, MARK

def handle_auto_entry(car_type):
    if car_type not in [WHITE, BLUE, MARK]:
        print("⚠️ 올바른 차량 종류가 아닙니다.", flush=True)
        return
    assign_parking(car_type)
    print_parking_status()
