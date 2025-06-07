import RPi.GPIO as GPIO
import time
from car_control import parking_zones, remove_parking, print_parking_status

sensor_pins = {
    'T1A': [{'TRIG': 23, 'ECHO': 24}, {'TRIG': 27, 'ECHO': 22}],
    'T1B': [{'TRIG': 17, 'ECHO': 18}, {'TRIG': 12, 'ECHO': 16}],
    'T2A': [{'TRIG': 13, 'ECHO': 19}, {'TRIG': 26, 'ECHO': 4}],
    'T2B': [{'TRIG': 7,  'ECHO': 1},  {'TRIG': 9,  'ECHO': 10}],
    '전기차': [{'TRIG': 15, 'ECHO': 2}, {'TRIG': 3,  'ECHO': 28}],
    '장애인': [{'TRIG': 31, 'ECHO': 32}, {'TRIG': 33, 'ECHO': 34}]
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for zone in sensor_pins:
    for sensor in sensor_pins[zone]:
        GPIO.setup(sensor['TRIG'], GPIO.OUT)
        GPIO.setup(sensor['ECHO'], GPIO.IN)
        GPIO.output(sensor['TRIG'], False)

time.sleep(2)

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

def detect_and_handle_exit():
    for zone in sensor_pins:
        for idx, sensor in enumerate(sensor_pins[zone]):
            dist = measure_distance(sensor['TRIG'], sensor['ECHO'])
            current_state = parking_zones[zone][idx]
            new_state = 1 if dist <= 25 else 0
            if current_state == 1 and new_state == 0:
                success = remove_parking(zone, idx + 1)
                if success:
                    print(f"📢 출차 감지: '{zone}' {idx + 1}번 자리", flush=True)
    print_parking_status()

def sensor_loop():
    try:
        while True:
            detect_and_handle_exit()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n프로그램 종료 중...", flush=True)
    finally:
        GPIO.cleanup()
