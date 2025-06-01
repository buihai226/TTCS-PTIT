from paddleocr import PaddleOCR
import cv2

def is_number(char):
    return char >= '0' and char <= '9'

def is_letter(char):
    return char >= 'A' and char <= 'Z'

paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')

def read_license_plate(image):
    """
    Đọc văn bản biển số xe từ ảnh sử dụng PaddleOCR.
    Input:
        image: Ảnh vùng biển số (numpy array từ OpenCV).
    Output:
        plate_text: Văn bản biển số (chuỗi).
    """
    ocr_results = paddle_ocr.ocr(image, cls=True)

    if not ocr_results or ocr_results[0] is None:
        return ""

    if len(ocr_results[0]) >= 2:
        line_1 = ocr_results[0][0][1][0]
        line_2 = ocr_results[0][1][1][0]
        plate_text = f"{line_1}\n{line_2}"
    else:
        plate_text = ocr_results[0][0][1][0]

    return plate_text

def format_license_plate(image):
    """
    Định dạng văn bản biển số xe theo quy tắc (số + chữ, dấu chấm).
    Input:
        image: Ảnh vùng biển số (numpy array từ OpenCV).
    Output:
        formatted_text: Văn bản biển số đã định dạng.
    """
    ocr_results = paddle_ocr.ocr(image, cls=True)

    if not ocr_results or ocr_results[0] is None:
        return ""

    formatted_text = ""
    for result in ocr_results[0]:
        text = result[1][0]
        if len(text) >= 3 and is_number(text[0]) and is_number(text[1]) and is_letter(text[2]):
            formatted_text += text
        elif '.' in text and 4 <= len(text) <= 6:
            formatted_text += f"\n{text}"

    return formatted_text