import cv2
import numpy as np
import pytesseract
import math
import pandas as pd
from gtts import gTTS
import os



def enhance_image(image):
    # 이미지 선명하게 하기 위한 필터 적용
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    return image


def post_process_image(image):
    # 추가적인 노이즈 제거 및 텍스트 영역 강조
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    # 모폴로지 연산을 통해 노이즈 제거
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    return image

def extract_text_from_image(image_path):
    # 이미지 읽기
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 히스토그램 평활화
    gray = cv2.equalizeHist(gray)
    # 명암 대비 조정
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    # 이미지 선명하게
    gray = enhance_image(gray)
    # 노이즈 제거를 위한 필터 적용
    gray = cv2.medianBlur(gray, 3)
    # 이진화
    _, img_bin = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 후처리
    img_bin = post_process_image(img_bin)

    # 텍스트 추출
    d = pytesseract.image_to_data(img_bin, lang='kor+eng', output_type=pytesseract.Output.DICT)
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        if d['text'][i].strip() != "":
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # 전처리된 이미지와 원본 이미지를 저장
    # 원본 이미지와 이진화 이미지를 동일한 크기로 조정
    img_resized = cv2.resize(img, (img_bin.shape[1], img_bin.shape[0]))
    combined_image_path = 'combined_image_with_text_8.jpg'
    combined_image = np.hstack((cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB), cv2.cvtColor(img_bin, cv2.COLOR_GRAY2RGB)))
    cv2.imwrite(combined_image_path, combined_image)

    # 이미지를 opencv로 열어줘서 잘 읽어오고 있는지 확인
    

    # 텍스트 추출 결과 반환
    text = pytesseract.image_to_string(img_bin, lang='kor+eng')
    return text, combined_image_path


def parse_nutrition_info(text):
    lines = text.split('\n')
    data = {'제품명': None, '탄수화물': None, '지방': None, '단백질': None, '식이섬유': None, '당류': None, '나트륨': None, '칼로리': None}

    for line in lines:
        if '제품명' in line:
            data['제품명'] = line.split(':')[-1].strip()
        elif '탄수화물' in line:
            data['탄수화물'] = line.split()[-1].strip()
        elif '지방' in line:
            data['지방'] = line.split()[-1].strip()
        elif '단백질' in line:
            data['단백질'] = line.split()[-1].strip()
        elif '식이섬유' in line:
            data['식이섬유'] = line.split()[-1].strip()
        elif '당류' in line:
            data['당류'] = line.split()[-1].strip()
        elif '나트륨' in line:
            data['나트륨'] = line.split()[-1].strip()
        elif '칼로리' in line:
            data['칼로리'] = line.split()[-1].strip()

    df = pd.DataFrame([data])
    return df


# 텍스트를 음성으로 변환
def text_to_speech(text, lang='ko'):
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    os.system("afplay output.mp3")  # OS에 맞게 변경 필요 (예: macOS의 경우 afplay, Windows의 경우 start)


def process_nutrition_label(image_path):
    extracted_text, combined_image_path = extract_text_from_image(image_path)
    print("Extracted Text:", extracted_text)
    nutrition_df = parse_nutrition_info(extracted_text)
    print(nutrition_df)

    nutrition_text = nutrition_df.to_string(index=False)
    text_to_speech(nutrition_text)
    return combined_image_path


# 테스트 이미지 경로
image_path = 'nutrition_label.jpg'
combined_image_path = process_nutrition_label(image_path)
print("Combined Image Path:", combined_image_path)
