import os
import shutil
import time
from fastapi import APIRouter, File, UploadFile, HTTPException, status

router = APIRouter(tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def secure_filename(filename: str) -> str:
    # simple security cleaning
    name, ext = os.path.splitext(filename)
    clean_name = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()
    if not clean_name:
        clean_name = "file"
    return f"{clean_name}_{int(time.time())}{ext.lower()}"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # construct the dynamic url
        # In a real environment, we'd read host/port from request headers or settings,
        # but since we are running locally at port 8000:
        url = f"/uploads/{filename}"
        return {"url": url, "filename": filename}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )

@router.post("/upload/cv")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CV must be a PDF file"
        )
    try:
        filepath = os.path.join(UPLOAD_DIR, "cv.pdf")
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"url": "/uploads/cv.pdf", "filename": "cv.pdf"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save CV: {str(e)}"
        )

@router.get("/upload/cv")
async def get_cv_status():
    filepath = os.path.join(UPLOAD_DIR, "cv.pdf")
    exists = os.path.exists(filepath)
    return {
        "exists": exists,
        "url": "/uploads/cv.pdf" if exists else None
    }
