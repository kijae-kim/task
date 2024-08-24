import cv2
import xml.etree.ElementTree as ET

# XML 파일 로드
tree = ET.parse('절도1.xml')
root = tree.getroot()

# 비디오 로드
cap = cv2.VideoCapture('절도1.mp4')

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
    color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))[::-1]
    label_colors[name] = color

# 프레임 카운터
frame_counter = 0

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
    drawn_labels = set()  # 이미 그려진 레이블을 추적

    for track in root.findall('.//track'):
        label = track.get('label')
        color = label_colors.get(label, (0, 255, 0))  # 기본 색상: 녹색

        for points in track.findall('points'):
            frame_number = int(points.get('frame'))
            if frame_number == frame_counter:
                # 좌표 추출
                pts_str = points.get('points').split(',')
                pts = [(int(float(pts_str[i]) * resize_scale), int(float(pts_str[i+1]) * resize_scale)) for i in range(0, len(pts_str), 2)]

                # 키포인트 그리기 및 동일 객체의 핀 연결
                if label not in drawn_labels:
                    for pt in pts:
                        cv2.circle(resized_frame, pt, 5, color, -1)
                    # 핀포인트들을 연결 (같은 색상으로)
                    for i in range(len(pts) - 1):
                        cv2.line(resized_frame, pts[i], pts[i+1], color, 2)
                    drawn_labels.add(label)  # 현재 레이블을 그려졌다고 표시

        # 바운딩 박스 그리기
        if track.find('object_article') is not None:
            for bbox in track.findall('object_article'):
                frame_number = int(bbox.get('frame'))
                if frame_number == frame_counter:
                    x1, y1, x2, y2 = [int(float(coord) * resize_scale) for coord in bbox.get('points').split(',')]
                    cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)  # 바운딩 박스 그리기

    # 프레임 표시
    cv2.imshow('Tracking', resized_frame)

    # 프레임 사이의 지연 시간 조절 (속도 조정)
    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

    frame_counter += 1  # 프레임 카운터 증가

cap.release()
cv2.destroyAllWindows()
