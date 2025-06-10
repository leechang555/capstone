import cv2
import numpy as np

def detect_color(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 파란색 영역 정의 (조금 넓힘)
    lower_blue = np.array([85, 30, 30])
    upper_blue = np.array([135, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_ratio = cv2.countNonZero(blue_mask) / (image.size / 3)

    # 초록색 (장애인 번호판)
    lower_green = np.array([40, 30, 30])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    green_ratio = cv2.countNonZero(green_mask) / (image.size / 3)

    print(f"🔵 blue_ratio: {blue_ratio:.2f}, 🟢 green_ratio: {green_ratio:.2f}")

    if green_ratio > 0.15:
        return "MARK"
    elif blue_ratio > 0.12:  # 기존보다 완화
        return "BLUE"
    else:
        return "WHITE"
