import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
import numpy as np
from ultralytics import YOLO
import os
from paddle_ocr import read_license_plate, format_license_plate

# Đường dẫn tới mô hình và ảnh
model_path = "C:/Users/Lenovo/Desktop/TTCS/TTCS-PTIT/src/backend/yolov8/train/weights/best.pt"
image_path = "C:/Users/Lenovo/Desktop/TTCS/TTCS-PTIT/src/img_test.jpg"

# Kiểm tra file tồn tại
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Không tìm thấy mô hình tại {model_path}")
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Không tìm thấy ảnh tại {image_path}")

# Load mô hình YOLOv8
model = YOLO(model_path)

def detect_objects(image_path):
    """Chạy phát hiện bằng YOLOv8."""
    try:
        results = model.predict(image_path, conf=0.5, iou=0.7)
        boxes = results[0].boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        confidences = results[0].boxes.conf.cpu().numpy()  # Độ tin cậy
        classes = results[0].boxes.cls.cpu().numpy()  # Lớp
        return boxes, confidences, classes, results[0].names
    except Exception as e:
        print(f"Lỗi khi chạy phát hiện: {e}")
        raise

# Lấy kết quả phát hiện
try:
    boxes, confidences, classes, class_names = detect_objects(image_path)
except Exception:
    exit()

# Đọc ảnh gốc
image = cv2.imread(image_path)
if image is None:
    raise ValueError(f"Không thể đọc ảnh từ {image_path}")
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Chuyển sang RGB

# Tạo figure và axes
fig, ax = plt.subplots(1, figsize=(12, 8))
ax.imshow(image_rgb)

# Tạo thư mục lưu kết quả
output_dir = "runs/detect"
os.makedirs(output_dir, exist_ok=True)

# Vẽ hộp giới hạn và xử lý vùng biển số
for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1
    
    # Tạo màu cho hộp giới hạn
    color = np.random.rand(3,)
    
    # Vẽ hình chữ nhật
    rect = patches.Rectangle((x1, y1), width, height, linewidth=2, edgecolor=color, facecolor='none')
    ax.add_patch(rect)
    
    # Cắt vùng biển số
    roi = image[int(y1):int(y2), int(x1):int(x2)]
    if roi.size == 0:
        print(f"Vùng cắt {i} rỗng, bỏ qua")
        continue
    
    # Đọc văn bản biển số
    license_text = read_license_plate(roi)
    if not license_text:
        license_text = format_license_plate(roi)
    if not license_text:
        license_text = "Not detected"
    
    # Thêm nhãn với lớp, độ tin cậy và văn bản biển số
    label = f"{class_names[int(cls)]}: {conf:.2f}\n{license_text}"
    ax.text(x1, y1 - 10, label, color=color, fontsize=12, 
            bbox=dict(facecolor='white', alpha=0.8), 
            verticalalignment='bottom')
    
    # Lưu vùng biển số
    crop_path = os.path.join(output_dir, f"license_plate_{i}.jpg")
    cv2.imwrite(crop_path, roi)
    print(f"Đã lưu vùng biển số tại: {crop_path}")

# Tắt trục
ax.axis('off')
plt.title('Kết quả nhận diện biển số xe')
result_path = os.path.join(output_dir, 'yolo_detection_result.png')
plt.savefig(result_path, bbox_inches='tight')
plt.show()

# In số lượng biển số và thông tin
print(f"Phát hiện {len(boxes)} biển số xe trong ảnh:")
for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
    roi = image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
    license_text = read_license_plate(roi)
    if not license_text:
        license_text = format_license_plate(roi)
    if not license_text:
        license_text = "Not detected"
    print(f"- Biển số {i+1}: {license_text}, Độ tin cậy: {conf:.2f}, Lớp: {class_names[int(cls)]}")