from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from yolov8_detect import detect_license_plate
from datetime import datetime
import logging
import os
import tempfile
from auth import init_db

# Import các module authentication
from auth import router as auth_router, get_current_user, UserDisplay, get_db_connection
from auth_routes import router as admin_router

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hệ thống Nhận Diện Biển Số Xe",
              description="API cho hệ thống nhận diện biển số xe sử dụng YOLOv8 và PaddleOCR",
              version="1.0.0")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm các router 
app.include_router(auth_router)
app.include_router(admin_router)

# Mount thư mục static
app.mount("/static", StaticFiles(directory="../static"), name="static")

@app.get("/")
async def root():
    return {
        "message": "API Hệ thống Nhận Diện Biển Số Xe",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/process")
async def process_image(
    file: UploadFile = File(...), 
    current_user: UserDisplay = Depends(get_current_user)
):
    """
    Xử lý ảnh hoặc video để nhận diện và đọc biển số xe.
    Input:
        file: File ảnh (.jpg, .png) hoặc video (.mp4).
    Output:
        JSON chứa danh sách các biển số được phát hiện: license_plate, confidence, timestamp.
    """
    try:
        # Kiểm tra định dạng file
        content_type = file.content_type
        if not content_type.startswith(("image/", "video/")):
            logger.error(f"File không phải ảnh hoặc video: {content_type}")
            raise HTTPException(status_code=400, detail="File phải là ảnh (jpg, png) hoặc video (mp4).")

        # Đọc file
        contents = await file.read()

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4" if content_type.startswith("video/") else ".jpg") as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name

        # Xử lý ảnh hoặc video
        detections = []
        if content_type.startswith("image/"):
            # Xử lý ảnh
            image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                logger.error("Không thể giải mã ảnh")
                raise HTTPException(status_code=400, detail="Không thể đọc ảnh.")

            # Tiền xử lý ảnh
            image = cv2.convertScaleAbs(image, alpha=1.2, beta=0)
            height, width = image.shape[:2]
            if max(height, width) < 640:
                scale = 640 / max(height, width)
                image = cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_LINEAR)
                logger.info(f"Ảnh đã được resize: {width}x{height} -> {int(width*scale)}x{int(height*scale)}")

            detections = detect_license_plate(image)
            logger.info(f"Phát hiện {len(detections)} biển số từ ảnh")

        else:
            # Xử lý video
            cap = cv2.VideoCapture(temp_file_path)
            if not cap.isOpened():
                logger.error(f"Không thể mở video: {temp_file_path}")
                raise HTTPException(status_code=400, detail="Không thể mở video.")

            frame_rate = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(frame_rate * 10)  # Lấy khung hình mỗi 10 giây
            frame_count = 0
            unique_plates = set()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if frame_count % frame_interval != 0:
                    continue

                # Tiền xử lý khung hình
                frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=0)
                height, width = frame.shape[:2]
                if max(height, width) < 640:
                    scale = 640 / max(height, width)
                    frame = cv2.resize(frame, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_LINEAR)

                frame_detections = detect_license_plate(frame)
                for det in frame_detections:
                    plate_text = det["text"] if det["text"] != "Error" else "Not detected"
                    if plate_text != "Not detected" and plate_text not in unique_plates:
                        unique_plates.add(plate_text)
                        detections.append(det)

                if len(detections) >= 10:  # Giới hạn số lượng phát hiện
                    break

            cap.release()
            logger.info(f"Phát hiện {len(detections)} biển số duy nhất từ video")

        # Xóa file tạm
        os.remove(temp_file_path)        # Chuẩn bị kết quả
        results = []
        for detection in detections:
            license_plate = detection["text"] if detection["text"] != "Error" else "Not detected"
            confidence = float(detection["confidence"])
            
            # Lưu kết quả vào database nếu có người dùng đăng nhập
            if current_user and license_plate != "Not detected":
                try:
                    connection = get_db_connection()
                    cursor = connection.cursor()
                    
                    # Lưu vào bảng detection_logs
                    query = """
                    INSERT INTO detection_logs 
                    (user_id, license_plate, confidence, timestamp, image_path) 
                    VALUES (%s, %s, %s, NOW(), %s)
                    """
                    cursor.execute(
                        query, 
                        (current_user.id, license_plate, confidence, temp_file_path if content_type.startswith("image/") else None)
                    )
                    connection.commit()
                    
                    logger.info(f"Đã lưu kết quả nhận diện vào DB: {license_plate}, user: {current_user.username}")
                except Exception as e:
                    logger.error(f"Lỗi khi lưu vào DB: {str(e)}")
                finally:
                    if 'cursor' in locals():
                        cursor.close()
                    if 'connection' in locals() and connection.is_connected():
                        connection.close()
            
            results.append({
                "license_plate": license_plate,
                "confidence": float(confidence * 100),
                "timestamp": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            })

        if not results:
            logger.warning("Không phát hiện được biển số")
            return {
                "detections": [],
                "message": "Không phát hiện được biển số",
                "timestamp": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            }

        return {
            "detections": results,
            "message": f"Phát hiện {len(results)} biển số",
            "timestamp": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Lỗi khi xử lý: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # init_db()
    get_db_connection()  # Kiểm tra kết nối DB khi khởi động
    uvicorn.run(app, host="0.0.0.0", port=8001)