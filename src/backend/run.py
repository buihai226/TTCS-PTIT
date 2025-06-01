import uvicorn
import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy thông tin cấu hình từ biến môi trường
host = os.getenv("API_HOST", "0.0.0.0")
port = int(os.getenv("API_PORT", 8001))
debug = os.getenv("DEBUG", "True").lower() in ["true", "1", "yes"]

if __name__ == "__main__":
    print(f"Khởi chạy ứng dụng trên http://{host}:{port}")
    print(f"Truy cập giao diện web tại: http://localhost:{port}/static/templates/index.html")
    print(f"Tài liệu API tại: http://localhost:{port}/docs")
    
    uvicorn.run(
        "app:app", 
        host=host, 
        port=port, 
        reload=debug
    )
