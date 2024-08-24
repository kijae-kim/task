import cv2
import numpy as np
import time
import pandas as pd
import pytesseract


def reorderPts(pts):
    idx = np.lexsort((pts[:, 1], pts[:, 0]))
    pts = pts[idx]

    if pts[0, 1] > pts[1, 1]:
        pts[[0, 1]] = pts[[1, 0]]

    if pts[2, 1] < pts[3, 1]:
        pts[[2, 3]] = pts[[3, 2]]

    return pts

def capture_nutrition_label(img, contours):
    dw, dh = 700, 400
    dstQuad = np.array([[0, 0], [0, dh], [dw, dh], [dw, 0]], np.float32)
    dst = np.zeros((dh, dw), np.uint8)

    for pts in contours:
        if cv2.contourArea(pts) < 1000:
            continue

        approx = cv2.approxPolyDP(pts, cv2.arcLength(pts, True) * 0.02, True)
        if len(approx) != 4:
            continue

        srcQuad = reorderPts(approx.reshape(4, 2).astype(np.float32))
        pers = cv2.getPerspectiveTransform(srcQuad, dstQuad)
        dst = cv2.warpPerspective(img, pers, (dw, dh))
        return dst

    return None

def extract_text_from_image(image):
    dst_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(dst_gray, lang='kor+eng')
    return text

# 인식한 텍스트에서 영양소 정보만 파싱해주는 함수
def parse_nutrition_info(text):
    nutrition_info = {
        'Carbohydrates': None,
        'Protein': None,
        'Fat': None
    }

    patterns = {
        'Carbohydrates': r'(탄수화물|Carbohydrates)\s*:\s*(\d+\.?\d*)\s*(g|grams|그램)',
        'Protein': r'(단백질|Protein)\s*:\s*(\d+\.?\d*)\s*(g|grams|그램)',
        'Fat': r'(지방|Fat)\s*:\s*(\d+\.?\d*)\s*(g|grams|그램)'
    }

    for nutrient, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nutrition_info[nutrient] = match.group(2)

    return nutrition_info

# iPhone 카메라 스트리밍 URL
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error")
    exit()

captured = False

while True:
    ret, img = cap.read()
    if not ret:
        print("Error: Failed")
        break

    src_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, src_bin = cv2.threshold(src_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(src_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    captured_image = capture_nutrition_label(img, contours)

    if captured_image is not None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        image_path = f"nutrition_label_{timestamp}.png"
        cv2.imwrite(image_path, captured_image)
        print(f"Images: {image_path}")

        extracted_text = extract_text_from_image(captured_image)
        print("text:")
        print(extracted_text)
        captured = True  # 한 번 캡처하면 더 이상 캡처하지 않도록 설정

    cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


# 데이터셋 저장.
df = pd.DataFrame(nutrition_data)
df.to_csv('nutrition_data.csv', index=False)
print("saved to nutrition_data.csv")

