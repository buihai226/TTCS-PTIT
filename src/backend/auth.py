from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import logging
import os

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("auth.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Router cho authentication
router = APIRouter(prefix="/api/auth", tags=["auth"])

# Tải biến môi trường từ .env
import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Cấu hình JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))

# Cấu hình kết nối MySQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "license_plate_db")
}

# Schema cho User
class User(BaseModel):
    id: Optional[int] = None
    fullname: str
    email: str
    username: str
    password: str
    role: str
    created_at: Optional[datetime] = None

class UserLogin(BaseModel):
    username: str
    password: str
    rememberMe: bool = False

class UserDisplay(BaseModel):
    id: int
    fullname: str
    email: str
    username: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserDisplay

# Hàm kết nối đến MySQL database
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        logger.error(f"Lỗi kết nối MySQL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể kết nối đến cơ sở dữ liệu"
        )

# Hàm khởi tạo database nếu chưa tồn tại
def init_db():
    print(12345)
    connection = None
    cursor = None
    try:
        # Kết nối đến server MySQL mà không chọn database
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        
        if not connection.is_connected():
            logger.error("Không thể kết nối đến MySQL Server")
            return
            
        cursor = connection.cursor()
        
        # Tạo database nếu chưa tồn tại
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Tạo bảng users nếu chưa tồn tại
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tạo bảng detection_logs nếu chưa tồn tại
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                license_plate VARCHAR(20),
                confidence FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path VARCHAR(255),
                vehicle_type VARCHAR(50),
                region VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
                       Insert into users (fullname, email, username, password, role)
                       values ('admin', 'admin@example.com', 'admin', 'admin123', 'admin')
        """)

        connection.commit()
        logger.info("Cơ sở dữ liệu đã được khởi tạo thành công")
    except Error as e:
        logger.error(f"Lỗi khởi tạo cơ sở dữ liệu: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# Gọi hàm khởi tạo khi chạy module
# init_db()

# Hàm tạo JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2 scheme cho token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hàm lấy user hiện tại từ token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin xác thực",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if user is None:
        raise credentials_exception
    
    return UserDisplay(
        id=user["id"],
        fullname=user["fullname"],
        email=user["email"],
        username=user["username"],
        role=user["role"]
    )

# API đăng ký user mới
@router.post("/register")
async def register_user(user: User):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Kiểm tra username đã tồn tại chưa
        cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đăng nhập đã tồn tại"
            )
        
        # Kiểm tra email đã tồn tại chưa
        cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
        
        # Hash mật khẩu
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Thêm user mới vào database
        cursor.execute(
            "INSERT INTO users (fullname, email, username, password, role) VALUES (%s, %s, %s, %s, %s)",
            (user.fullname, user.email, user.username, hashed_password.decode('utf-8'), user.role)
        )
        connection.commit()
        
        logger.info(f"User mới đã đăng ký: {user.username}")
        
        return {
            "success": True,
            "message": "Đăng ký thành công"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Lỗi đăng ký user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Đăng ký thất bại: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()

# API đăng nhập
@router.post("/login")
async def login(user_login: UserLogin):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Tìm user theo username
        cursor.execute("SELECT * FROM users WHERE username = %s", (user_login.username,))
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"Đăng nhập thất bại - User không tồn tại: {user_login.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Thông tin đăng nhập không chính xác"
            )
        
        # Kiểm tra mật khẩu
        if not bcrypt.checkpw(user_login.password.encode('utf-8'), user["password"].encode('utf-8')):
            logger.warning(f"Đăng nhập thất bại - Mật khẩu không đúng: {user_login.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Thông tin đăng nhập không chính xác"
            )
        
        # Tạo token với thời gian hết hạn dài hơn nếu rememberMe=True
        access_token_expires = timedelta(days=30) if user_login.rememberMe else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Đăng nhập thành công: {user_login.username}")
        
        return {
            "success": True,
            "token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "fullname": user["fullname"],
                "email": user["email"],
                "username": user["username"],
                "role": user["role"]
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Lỗi đăng nhập: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Đăng nhập thất bại: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()

# API kiểm tra token và lấy thông tin user
@router.get("/me")
async def get_user_info(current_user: UserDisplay = Depends(get_current_user)):
    return {
        "success": True,
        "user": current_user
    }

# API đăng xuất (client-side only)
@router.post("/logout")
async def logout():
    return {
        "success": True,
        "message": "Đăng xuất thành công"
    }
