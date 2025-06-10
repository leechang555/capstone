import torch
import cv2
import easyocr
from color_detector import detect_color

class LicensePlateDetector:
    def __init__(self):
        # lp_det.pt 또는 yolov5s.pt 경로에 맞게 설정
        self.model = torch.hub.load(
            'ultralytics/yolov5',
            'custom',
            path='lp_det.pt',   # ← 여기에 사용하는 모델명 적기
            force_reload=True
        )
        self.reader = easyocr.Reader(['en'])  # 번호판 텍스트 읽기용

    def detect_from_frame(self, frame):
        results = self.model(frame)
        result_list = []

        for *box, conf, cls in results.xyxy[0]:
            x1, y1, x2, y2 = map(int, box)
            cropped = frame[y1:y2, x1:x2]

            if cropped.size == 0:
                continue

            # 번호판 텍스트 (선택)
            ocr_result = self.reader.readtext(cropped)
            plate_number = ocr_result[0][1] if ocr_result else "인식 실패"

            # 색상 분류
            label = detect_color(cropped)

            # 시각화
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{plate_number} ({label})",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            result_list.append((plate_number, label))

        return frame, result_list
