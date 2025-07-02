import json
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional

from sqlalchemy import desc
from database import SuipMetadata, get_db
from parser import upload_and_parse_file
from sqlalchemy.orm import Session

app = FastAPI()

SUIP_URL = "https://suip.biz/ru/?act=mat"


@app.get("/")
def index():
    return "Hi"


@app.post("/suip-data/parse")
def parse_suip_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    result = upload_and_parse_file(file, url=SUIP_URL)
    entry = SuipMetadata(filename=file.filename, file_metadata=result)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return JSONResponse(
        content={
            "id": entry.id,
            "filename": entry.filename,
            "metadata": entry.file_metadata,
        }
    )


@app.get("/suip-data")
async def get_suip_data(
    filename: Optional[str] = Query(
        None, description="Filter by filename (partial match)"
    ),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(SuipMetadata)

    if filename:
        query = query.filter(SuipMetadata.filename.ilike(f"%{filename}%"))

    total = query.count()
    items = (
        query.order_by(desc(SuipMetadata.created_at)).offset(offset).limit(limit).all()
    )

    return {
        "total": total,
        "items": [
            {
                "id": item.id,
                "filename": item.filename,
                "metadata": item.file_metadata,
                "created_at": item.created_at.isoformat(),
                "save_report": f"/suip-data/{item.id}/report",
            }
            for item in items
        ],
    }


@app.get("/suip-data/{item_id}/report")
async def download_report(item_id: int, db: Session = Depends(get_db)):
    entry = db.query(SuipMetadata).filter(SuipMetadata.id == item_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Report not found")

    # Создаём временный файл
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".json", mode="w", encoding="utf-8"
    ) as tmp:
        json.dump(
            {
                "id": entry.id,
                "filename": entry.filename,
                "created_at": entry.created_at.isoformat(),
                "metadata": entry.file_metadata,
            },
            tmp,
            ensure_ascii=False,
            indent=2,
        )
        tmp_path = tmp.name

    return FileResponse(
        path=tmp_path,
        media_type="application/json",
        filename=f"suip_report_{entry.id}.json",
    )
