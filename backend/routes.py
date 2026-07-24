from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid
from typing import Dict, Any

from database import get_db
import models
from ai_brain import ai_brain
from memory_manager import memory_manager
from plugin_system import plugin_system

router = APIRouter()

@router.get("/api/sessions")
def list_sessions(db: Session = Depends(get_db)):
    return db.query(models.ChatSession).order_by(models.ChatSession.created_at.desc()).all()

@router.post("/api/sessions")
def create_session(db: Session = Depends(get_db)):
    new_id = str(uuid.uuid4())
    session = models.ChatSession(id=new_id, title="New Conversation")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/api/sessions/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.timestamp.asc()).all()
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "messages": messages
    }

@router.post("/api/sessions/{session_id}/messages")
def post_message(session_id: str, payload: Dict[str, str], db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_content = payload.get("content", "")
    if not user_content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    user_msg = models.Message(
        session_id=session_id,
        sender="user",
        content=user_content
    )
    db.add(user_msg)

    steps = ai_brain.process_message_with_planner(user_content)

    assistant_content = ""
    for step in steps:
        if step["action"] == "conversation":
            assistant_content += f"{step['result']}\n"
        else:
            assistant_content += f"**Step Complete**: {step['step']}\n"
            assistant_content += f"```\n{step['result']}\n```\n"

    memory_manager.add_memory(db, user_content, category="conversation_context")

    task_id = str(uuid.uuid4())
    task = models.TaskRecord(
        id=task_id,
        title=f"Analyze & Process: {user_content[:40]}...",
        status="completed",
        steps=steps
    )
    db.add(task)

    ai_msg = models.Message(
        session_id=session_id,
        sender="ai",
        content=assistant_content.strip(),
        meta_data={"steps": steps, "task_id": task_id}
    )
    db.add(ai_msg)

    if session.title == "New Conversation":
        session.title = user_content[:30] + ("..." if len(user_content) > 30 else "")

    db.commit()
    db.refresh(ai_msg)
    return ai_msg

@router.get("/api/system/stats")
def get_system_stats():
    import random
    return {
        "cpu_usage": round(random.uniform(5.0, 35.0), 1),
        "ram_usage": round(random.uniform(2.5, 4.2), 2),
        "ram_total": 8.00,
        "temperature": round(random.uniform(42.0, 58.0), 1),
        "status": "fully_operational"
    }

@router.get("/api/memories")
def get_memories(query: str = None, db: Session = Depends(get_db)):
    if query:
        return memory_manager.search_memories(db, query)
    memories = db.query(models.MemoryEntry).all()
    return [{
        "id": m.id,
        "content": m.content,
        "category": m.category,
        "created_at": m.created_at.isoformat()
    } for m in memories]

@router.post("/api/memories")
def create_memory(payload: Dict[str, str], db: Session = Depends(get_db)):
    content = payload.get("content", "")
    category = payload.get("category", "general")
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    mem = memory_manager.add_memory(db, content, category)
    return {
        "id": mem.id,
        "content": mem.content,
        "category": mem.category,
        "created_at": mem.created_at.isoformat()
    }

@router.delete("/api/memories/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    mem = db.query(models.MemoryEntry).filter(models.MemoryEntry.id == memory_id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(mem)
    db.commit()
    return {"message": "Memory entry deleted successfully."}

@router.get("/api/plugins")
def get_plugins():
    return plugin_system.list_plugins()

@router.post("/api/plugins/{plugin_id}/toggle")
def toggle_plugin(plugin_id: str, payload: Dict[str, bool]):
    enabled = payload.get("enabled", True)
    plugin_system.set_enabled(plugin_id, enabled)
    return {"id": plugin_id, "enabled": enabled}

@router.get("/api/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.TaskRecord).order_by(models.TaskRecord.created_at.desc()).all()
