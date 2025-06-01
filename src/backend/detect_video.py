import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
import logging
from paddle_ocr import read_license_plate, format_license_plate

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("video_detection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Thêm biến môi trường để tránh lỗi OMP
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Đường dẫn tới mô hình
model_path = "C:/Users/Lenovo/Desktop/TTCS/TTCS-PTIT/src/backend/yolov8/train/weights/best.pt"

# Đường dẫn tới video (.mp4 trong thư mục cùng cấp)
video_path = "C:/Users/Lenovo/Desktop/TTCS/TTCS-PTIT/src/static/video_test.mp4"  # Thay bằng tên file video của bạn, ví dụ: "my_video.mp4"

# Kiểm tra file mô hình
if not os.path.exists(model_path):
    logger.error(f"Không tìm thấy mô hình tại {model_path}")
    raise FileNotFoundError(f"Không tìm thấy mô hình tại {model_path}")

# Kiểm tra file video
if not os.path.exists(video_path):
    logger.error(f"Không tìm thấy file video tại {video_path}")
    raise FileNotFoundError(f"Không tìm thấy file video tại {video_path}")

# Load mô hình YOLOv8
try:
    logger.info("Đang tải mô hình YOLOv8")
    model = YOLO(model_path)
except Exception as e:
    logger.error(f"Lỗi khi tải mô hình YOLOv8: {e}")
    exit()

# Mở video
try:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Không thể mở video: {video_path}")
        raise ValueError(f"Không thể mở video: {video_path}")
except Exception as e:
    logger.error(f"Lỗi khi mở video: {e}")
    exit()

# Tạo thư mục lưu vùng cắt
output_dir = "runs/detect"
os.makedirs(output_dir, exist_ok=True)

# Khởi tạo Matplotlib
fig, ax = plt.subplots(1, figsize=(12, 8))
plt.ion()  # Bật chế độ tương tác

prev_frame_time = 0
list_read_plates = set()  # Lưu danh sách biển số đã đọc

while True:
    ret, frame = cap.read()
    if not ret:
        logger.warning("Hết video hoặc không thể đọc khung hình")
        break

    # Chuyển frame sang RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Phát hiện biển số
    try:
        results = model.predict(frame_rgb, conf=0.50, iou=0.7, imgsz=640)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        class_names = results[0].names
        logger.info(f"Phát hiện {len(boxes)} biển số trong khung hình")
    except Exception as e:
        logger.error(f"Lỗi khi chạy phát hiện: {e}")
        continue

    # Xóa nội dung khung hình trước
    ax.clear()
    ax.imshow(frame_rgb)
    
    # Xử lý từng biển số
    for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1

        # Tạo màu ngẫu nhiên
        color = np.random.rand(3,)

        # Vẽ hộp giới hạn
        rect = patches.Rectangle((x1, y1), width, height, linewidth=2, edgecolor=color, facecolor='none')
        ax.add_patch(rect)

        # Cắt vùng biển số
        roi = frame[int(y1):int(y2), int(x1):int(x2)]
        if roi.size == 0:
            logger.warning(f"Vùng cắt {i} rỗng, bỏ qua")
            license_text = "Not detected"
        else:
            # Đọc văn bản biển số
            try:
                license_text = read_license_plate(roi)
                logger.info(f"Biển số thô {i+1}: {license_text}")
                if not license_text:
                    license_text = format_license_plate(roi)
                    logger.info(f"Biển số định dạng {i+1}: {license_text}")
                if not license_text:
                    license_text = "Not detected"
                list_read_plates.add(license_text)
            except Exception as e:
                logger.error(f"Lỗi khi đọc biển số {i+1}: {e}")
                license_text = "Not detected"

            # Lưu vùng cắt
            crop_path = os.path.join(output_dir, f"license_plate_{i}_{int(time.time())}.jpg")
            cv2.imwrite(crop_path, roi)
            logger.info(f"Đã lưu vùng biển số tại: {crop_path}")

        # Thêm nhãn
        label = f"{class_names[int(cls)]}: {conf:.2f}\n{license_text}"
        ax.text(x1, y1 - 10, label, color=color, fontsize=12, 
                bbox=dict(facecolor='white', alpha=0.8), 
                verticalalignment='bottom')

    # Tính và hiển thị FPS
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time) if prev_frame_time > 0 else 0
    prev_frame_time = new_frame_time
    ax.text(10, 50, f"FPS: {int(fps)}", color='green', fontsize=14, 
            bbox=dict(facecolor='white', alpha=0.8))

    # Cập nhật khung hình
    ax.axis('off')
    plt.title('Nhận diện biển số xe từ video')
    plt.draw()
    plt.pause(0.01)  # Tạm dừng ngắn để mô phỏng video

    # Thoát bằng phím 'q'
    if plt.waitforbuttonpress(timeout=0.001):
        key = plt.get_current_fig_manager().canvas.key_press_event
        if key == 'q':
            logger.info("Thoát bởi người dùng")
            break

# Giải phóng tài nguyên
cap.release()
plt.close(fig)
logger.info("Đã dừng nhận diện video")