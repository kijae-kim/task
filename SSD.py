import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

import kagglehub

# Download latest version
path = kagglehub.model_download("tensorflow/ssd-mobilenet-v2/tensorFlow2/ssd-mobilenet-v2")

print("Path to model files:", path)
# 모델을 로컬로 다운로드하고 로드
# model_url = 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2'
# model_dir = '/Users/gimgijae/Desktop/KDT/CV/pythonProject/ssd-mobilenet-v2-tensorflow2-ssd-mobilenet-v2-v1/saved_model.pb'  # 모델을 저장할 디렉터리

# 모델 다운로드
model = hub.load(path)

# 웹캠 캡처
cap = cv2.VideoCapture(0)

def detect_objects(frame):
    input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)
    detector_output = model(input_tensor)
    return detector_output

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 객체감지
    detections = detect_objects(frame)

    num_detections = int(detections['num_detections'])
    detection_boxes = detections['detection_boxes'][0].numpy()  # 바운딩 박스
    detection_classes = detections['detection_classes'][0].numpy().astype(int)  # 클래스
    detection_scores = detections['detection_scores'][0].numpy()  # 점수

    # 신뢰도 임계값 설정
    confidence_threshold = 0.5

    # 감지된 객체 그리기
    for i in range(num_detections):
        if detection_scores[i] >= confidence_threshold:
            box = detection_boxes[i]
            ymin, xmin, ymax, xmax = box

            # 원본 이미지 크기로 변환
            (left, right, top, bottom) = (xmin * frame.shape[1], xmax * frame.shape[1],
                                          ymin * frame.shape[0], ymax * frame.shape[0])

            # 바운딩 박스 그리기
            cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)  # 초록색

            # 클래스 레이블
            class_id = int(detection_classes[i])
            label = f'{class_id}: {detection_scores[i]:.2f}'

            # 레이블 표시
            cv2.putText(frame, label, (int(left), int(top) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 결과 화면에 표시
    cv2.imshow('SSD 손 제스쳐', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()