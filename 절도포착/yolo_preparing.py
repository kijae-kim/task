from ultralytics import YOLO
import cv2
import numpy as np

# YOLO 모델 로드 (pose estimation 모델)
model = YOLO('yolov8n-pose.pt')  # 또는 'yolov8s-pose.pt', 'yolov8m-pose.pt', 'yolov8l-pose.pt', 'yolov8x-pose.pt'

# 비디오 캡처 객체 생성
video_path = "/Users/gimgijae/Desktop/KDT/CV/절도포착/절도1.mp4"
cap = cv2.VideoCapture(video_path)

# 비디오 속성 가져오기
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# 출력 비디오 설정
output_path = '/Users/gimgijae/Desktop/KDT/CV/절도포착/절도1.mp4'
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

while cap.isOpened():
    # 프레임 읽기
    success, frame = cap.read()

    if success:
        # YOLO로 포즈 예측
        results = model(frame)
        
        # 결과 시각화
        annotated_frame = results[0].plot()
        
        # 추가적인 시각화 (예: 키포인트 연결)
        for result in results:
            keypoints = result.keypoints.xy[0].cpu().numpy()
            for kp in keypoints:
                if kp[0] > 0 and kp[1] > 0:  # 유효한 키포인트만 그리기
                    cv2.circle(annotated_frame, (int(kp[0]), int(kp[1])), 5, (0, 255, 0), -1)
            
            # 키포인트 연결 (예시)
            connections = [(0,1), (1,3), (0,2), (2,4), (5,6), (5,7), (7,9), (6,8), (8,10)]
            for connection in connections:
                start_point = keypoints[connection[0]]
                end_point = keypoints[connection[1]]
                if start_point[0] > 0 and start_point[1] > 0 and end_point[0] > 0 and end_point[1] > 0:
                    cv2.line(annotated_frame, 
                             (int(start_point[0]), int(start_point[1])), 
                             (int(end_point[0]), int(end_point[1])), 
                             (255, 0, 0), 2)

        # 프레임 표시
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        
        # 결과 비디오에 프레임 쓰기
        out.write(annotated_frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

# 자원 해제
cap.release()
out.release()
cv2.destroyAllWindows()