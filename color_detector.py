import cv2
import numpy as np

# 차량 타입 약어 정의
WHITE = "WHITE"
BLUE = "BLUE"
MARK = "MARK"

def detect_color(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 파란색 탐지
    lower_blue = np.array([85, 30, 30])
    upper_blue = np.array([135, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_ratio = cv2.countNonZero(blue_mask) / (image.size / 3)

    # 초록색 탐지
    lower_green = np.array([40, 30, 30])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    green_ratio = cv2.countNonZero(green_mask) / (image.size / 3)

    print(f"🔵 blue_ratio: {blue_ratio:.2f}, 🟢 green_ratio: {green_ratio:.2f}")

    if green_ratio > 0.25:
        print("🎨 색상: 장애인 차량")
        return MARK
    elif blue_ratio > 0.8:
        print("🎨 색상: 전기 차량")
        return BLUE
    else:
        print("🎨 색상: 일반 차량")
        return WHITE
