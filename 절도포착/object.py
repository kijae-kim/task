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
    color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))[::-1]
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
    for track in root.findall('.//track'):
        label = track.get('label')
        color = label_colors.get(label, (0, 255, 0))  # 기본 색상: 녹색

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

    # 프레임 표시
    cv2.imshow('Tracking', resized_frame)

    # 프레임 사이의 지연 시간 조절 (속도 조정)
    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

    frame_counter += 1  # 프레임 카운터 증가

cap.release()
cv2.destroyAllWindows()
