from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import json
import datetime
from typing import List

from database import get_db, engine, Base
from logger_service import log_event
import models
from routes import router

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JARVIS Personal AI Operating System API",
    description="The foundational API for the JARVIS Personal AI OS, providing AI reasoning, planning, memory, and actions.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        log_event("WebSocket", f"Client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            log_event("WebSocket", f"Client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "received": parsed
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    log_event("System", "JARVIS System Startup Completed. Ready for execution.")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "JARVIS Personal AI OS",
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/api/logs")
def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(models.SystemLog).order_by(models.SystemLog.timestamp.desc()).limit(limit).all()
    return logs

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
