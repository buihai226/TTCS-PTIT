from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
import logging
from auth import get_db_connection, get_current_user, UserDisplay

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("admin.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Router cho admin API
router = APIRouter(prefix="/api/admin", tags=["admin"])

# Model cho dashboard statistics
class DashboardStats(BaseModel):
    totalDetections: int
    totalUsers: int
    todayDetections: int
    accuracyRate: float

# Model cho detection
class Detection(BaseModel):
    id: int
    license_plate: str
    confidence: float
    timestamp: str
    username: str

# Model cho dashboard response
class DashboardResponse(BaseModel):
    success: bool
    stats: DashboardStats
    recentDetections: List[Detection]

# API lấy thông tin dashboard
@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(current_user: UserDisplay = Depends(get_current_user)):
    # Kiểm tra quyền admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập"
        )
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Lấy tổng số lượt nhận diện
        cursor.execute("SELECT COUNT(*) as total FROM detection_logs")
        total_detections = cursor.fetchone().get("total", 0)
        
        # Lấy tổng số người dùng
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone().get("total", 0)
        
        # Lấy số lượt nhận diện trong ngày
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(f"SELECT COUNT(*) as total FROM detection_logs WHERE DATE(timestamp) = '{today}'")
        today_detections = cursor.fetchone().get("total", 0)
        
        # Lấy độ chính xác trung bình
        cursor.execute("SELECT AVG(confidence) as avg_confidence FROM detection_logs")
        avg_confidence = cursor.fetchone().get("avg_confidence", 0)
        if avg_confidence is None:
            avg_confidence = 0
        
        # Lấy các lượt nhận diện gần đây
        cursor.execute("""
            SELECT dl.id, dl.license_plate, dl.confidence, 
                   DATE_FORMAT(dl.timestamp, '%d/%m/%Y, %H:%i:%s') as formatted_timestamp,
                   u.username
            FROM detection_logs dl
            LEFT JOIN users u ON dl.user_id = u.id
            ORDER BY dl.timestamp DESC
            LIMIT 10
        """)
        recent_detections = cursor.fetchall()
        
        # Chuẩn bị data cho response
        stats = DashboardStats(
            totalDetections=total_detections,
            totalUsers=total_users,
            todayDetections=today_detections,
            accuracyRate=float(avg_confidence * 100) if avg_confidence else 0
        )
        
        detections = []
        for detection in recent_detections:
            detections.append(Detection(
                id=detection["id"],
                license_plate=detection["license_plate"] or "Unknown",
                confidence=float(detection["confidence"] * 100) if detection["confidence"] else 0,
                timestamp=detection["formatted_timestamp"],
                username=detection["username"] or "System"
            ))
        
        return {
            "success": True,
            "stats": stats,
            "recentDetections": detections
        }
        
    except Exception as e:
        logger.error(f"Lỗi lấy dữ liệu dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy dữ liệu dashboard: {str(e)}"
        )
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
