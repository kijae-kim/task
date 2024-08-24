import cv2
import xml.etree.ElementTree as ET


# XML 파일 파싱
def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    theft_segments = []

    for segment in root.findall(".//segment"):
        start_frame = int(segment.find('start').text)
        stop_frame = int(segment.find('stop').text)
        theft_segments.append((start_frame, stop_frame))

    return theft_segments


# 비디오 클립 추출
def extract_video_clips(video_file, segments, output_folder):
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)

    for i, (start_frame, stop_frame) in enumerate(segments):
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # 비디오 저장을 위한 설정
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(f'{output_folder}/theft_clip_{i}.mp4', fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

        for frame_num in range(start_frame, stop_frame + 1):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        out.release()

    cap.release()


# 파일 경로
xml_file = '절도1.xml'
video_file = '절도1.mp4'
output_folder = 'C:\Sarr\KDT\CV\절도포착'

# XML 파일에서 절도 장면 구간 가져오기
segments = parse_xml(xml_file)

# 비디오 파일에서 절도 장면 추출하기
extract_video_clips(video_file, segments, output_folder)

print("영상 클립 추출 완료.")
