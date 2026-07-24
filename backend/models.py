from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False) # "user" or "ai" or "system"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    meta_data = Column(JSON, nullable=True)

    session = relationship("ChatSession", back_populates="messages")

class MemoryEntry(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False) # Floating point vector array
    category = Column(String, default="general") # "user_preference", "fact"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TaskRecord(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="pending") # "pending", "running", "completed", "failed"
    steps = Column(JSON, nullable=False) # Array of objects: { step: str, status: str, result: str }
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, default="INFO")
    module = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PluginRecord(Base):
    __tablename__ = "plugins"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
