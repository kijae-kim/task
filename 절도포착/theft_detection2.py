import cv2
import xml.etree.ElementTree as ET
import time
import os

# XML 파일 로드
tree = ET.parse('/Users/gimgijae/Desktop/KDT/CV/절도포착/절도1.xml')
root = tree.getroot()

# 비디오 로드
cap = cv2.VideoCapture('/Users/gimgijae/Desktop/KDT/CV/절도포착/절도1.mp4')

# 초당 프레임 수 (FPS)
fps = int(cap.get(cv2.CAP_PROP_FPS))

# 프레임 간 지연 시간 (밀리초 단위)
delay = int(1000 / fps * 0.7)  # 비디오 속도를 약 70%로 줄임

# 프레임 크기 조정 비율
resize_scale = 0.5

# 레이블 색상 저장
label_colors = {}
for label in root.findall('.//label'):
    name = label.find('name').text
    color = label.find('color').text
    # 색상을 BGR 포맷으로 변환
    color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))[::-1]
    label_colors[name] = color

# 프레임 카운터
frame_counter = 0

# 출력 설정
output_folder = 'KDT/절도포착/theft/'
os.makedirs(output_folder, exist_ok=True)
timestamp_file_path = os.path.join(output_folder, 'theft_timestamps.txt')

# 도난 감지 관련 변수
last_theft_time = 0
theft_cooldown = 5  # 도난 감지 간 최소 시간 간격 (초)

# 관절을 선으로 연결할 순서 정의
skeleton_connections = {
    "Right foot": ["Right knee"],
    "Right knee": ["Right  hip"],
    "Right  hip": ["Left hip"],  # 몸통 가운데 연결
    "Left hip": ["Left knee"],
    "Left knee": ["Left foot"],
    "Right shoulder": ["Right  hip", "Left shoulder"],  # Right shoulder와 Left shoulder 연결 추가
    "Left shoulder": ["Left hip"],
    "Right hand": ["Right shoulder"],
    "Left hand": ["Left shoulder"]
}

with open(timestamp_file_path, 'w') as timestamp_file:
    # 비디오의 프레임을 반복하면서 처리
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 프레임 크기 조정
        height, width = frame.shape[:2]
        new_dim = (int(width * resize_scale), int(height * resize_scale))
        resized_frame = cv2.resize(frame, new_dim, interpolation=cv2.INTER_AREA)

        # XML에서 특정 프레임의 주석 확인
        keypoints = {}
        theft_detected = False

        for track in root.findall('.//track'):
            label = track.get('label')
            color = label_colors.get(label, (0, 255, 0))  # 기본 색상: 녹색

            # 필요한 관절만 처리
            if label in skeleton_connections.keys() or label in [item for sublist in skeleton_connections.values() for
                                                                 item in sublist]:
                for points in track.findall('points'):
                    frame_number = int(points.get('frame'))
                    if frame_number == frame_counter:
                        # 좌표 추출
                        pts_str = points.get('points').split(',')
                        pt = (int(float(pts_str[0]) * resize_scale), int(float(pts_str[1]) * resize_scale))
                        keypoints[label] = pt
                        # 키포인트 그리기
                        cv2.circle(resized_frame, pt, 5, color, -1)
                        theft_detected = True

            # 바운딩 박스 처리
            for box in track.findall('box'):
                frame_number = int(box.get('frame'))
                if frame_number == frame_counter:
                    # 바운딩 박스 좌표 추출 및 크기 조정
                    xtl = int(float(box.get('xtl')) * resize_scale)
                    ytl = int(float(box.get('ytl')) * resize_scale)
                    xbr = int(float(box.get('xbr')) * resize_scale)
                    ybr = int(float(box.get('ybr')) * resize_scale)

                    # 바운딩 박스 그리기
                    cv2.rectangle(resized_frame, (xtl, ytl), (xbr, ybr), color, 2)
                    theft_detected = True

        # 도난 감지 및 기록
        current_time = time.time()
        if theft_detected and (current_time - last_theft_time > theft_cooldown):
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            print(f"Theft detected at frame {frame_counter}, time: {timestamp:.2f} seconds")
            cv2.putText(resized_frame, "THEFT DETECTED!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 타임스탬프 기록
            timestamp_file.write(f"Theft detected at frame {frame_counter}, time: {timestamp:.2f} seconds\n")
            timestamp_file.flush()  # 즉시 파일에 쓰기

            last_theft_time = current_time

        # 관절 연결
        for start_point, end_points in skeleton_connections.items():
            if start_point in keypoints:
                for end_point in end_points:
                    if end_point in keypoints:
                        cv2.line(resized_frame, keypoints[start_point], keypoints[end_point], (255, 0, 0), 2)

        # 프레임 표시
        cv2.imshow('Tracking', resized_frame)

        # 프레임 사이의 지연 시간 조절 (속도 조정)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

        frame_counter += 1  # 프레임 카운터 증가

cap.release()
cv2.destroyAllWindows()