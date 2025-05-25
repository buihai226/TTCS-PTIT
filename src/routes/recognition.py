from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import JSONResponse
import requests
import os
import shutil

router = APIRouter()

COLAB_API_URL = "https://xxxx.ngrok.io/process"  # Thay bằng URL từ ngrok

@router.post("/recognize")
async def recognize_plate(file: UploadFile = File(...)):
    upload_dir = "src/static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(file_path, "rb") as f:
        files = {"file": (file.filename, f)}
        response = requests.post(COLAB_API_URL, files=files)
        result = response.json()

    os.remove(file_path)
    return JSONResponse(content={"plate": result["plate"]})