import cv2
import numpy as np
from ultralytics import YOLO
import os
from paddle_ocr import read_license_plate, format_license_plate

def create_padding(original_image):
    """
    Thêm padding (10 pixel mỗi phía) cho vùng cắt để tăng kích thước.
    Input:
        original_image: Ảnh vùng cắt (numpy array từ OpenCV).
    Output:
        padded_image: Ảnh sau khi thêm padding.
    """
    if original_image is None or original_image.size == 0:
        print("Error: Could not read the image in create_padding")
        return None
    
    height, width, channels = original_image.shape
    top_padding = 10
    bottom_padding = 10
    left_padding = 10
    right_padding = 10
    
    padded_image = cv2.copyMakeBorder(
        original_image,
        top_padding, bottom_padding, left_padding, right_padding,
        borderType=cv2.BORDER_CONSTANT,
        value=[0, 0, 0]  # Padding màu đen
    )
    
    return padded_image

def detect_license_plate(image, model_path="C:/Users/Lenovo/Desktop/TTCS/TTCS-PTIT/src/backend/yolov8/train/weights/best.pt"):
    """
    Nhận diện và đọc biển số xe trong ảnh sử dụng YOLOv8 và PaddleOCR.
    Input:
        image: Ảnh đầu vào (numpy array từ OpenCV).
        model_path: Đường dẫn đến file trọng số YOLOv8 (best.pt).
    Output:
        detections: Danh sách các vùng biển số, mỗi vùng chứa tọa độ [x, y, w, h], độ tin cậy, và văn bản.
    """
    # Kiểm tra file mô hình tồn tại
    if not os.path.exists(model_path):
        print(f"Lỗi: Không tìm thấy mô hình tại {model_path}")
        return []

    try:
        # Load mô hình YOLOv8
        model = YOLO(model_path)
    except Exception as e:
        print(f"Lỗi khi tải mô hình YOLOv8: {e}")
        return []

    # Chuyển ảnh sang định dạng RGB và dự đoán
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    try:
        results = model.predict(img_rgb, conf=0.3, iou=0.7)  # Ngưỡng conf và iou có thể điều chỉnh
    except Exception as e:
        print(f"Lỗi khi chạy inference YOLOv8: {e}")
        return []

    detections = []
    boxes = results[0].boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2], chỉ lấy vùng phát hiện đầu tiên
    confidences = results[0].boxes.conf.cpu().numpy()  # Độ tin cậy
    print(f"Số lượng vùng phát hiện được: {len(boxes)}")  # Debug: Số vùng phát hiện

    if len(boxes) == 0:
        print("Không phát hiện được biển số xe bởi YOLOv8")
        return []

    for i, (box, conf) in enumerate(zip(boxes, confidences)):
        x1, y1, x2, y2 = map(float, box[:4])
        print(f"Vùng phát hiện {i+1}: x1={x1}, y1={y1}, x2={x2}, y2={y2}, confidence={conf:.2f}")  # Debug: Thông tin vùng
        x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
        
        # Cắt vùng biển số và thêm padding
        cropped_img = image[int(y1):int(y2), int(x1):int(x2)]
        if cropped_img.size == 0:
            print(f"Vùng cắt {i+1} rỗng, bỏ qua")
            continue
        padded_img = create_padding(cropped_img)
        if padded_img is None:
            continue

        # Đọc văn bản bằng PaddleOCR
        text = read_license_plate(padded_img)
        if not text:
            text = format_license_plate(paddeqqd_img)
        if not text:
            text = "Error"

        detections.append({
            "bbox": [x, y, w, h],
            "confidence": conf,
            "text": text
        })

    return detections