"""SQLite storage: one user, saved charts, known events."""
from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import (JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text,
                        create_engine)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

DB_URL = os.environ.get("KP_DB_URL", "sqlite:///" + os.path.join(os.path.dirname(__file__), "..", "kp.db"))
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)


class ChartRec(Base):
    __tablename__ = "charts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(120), nullable=False)
    birth_local = Column(String(32), nullable=False)       # ISO local date-time, no offset
    tz = Column(String(64), nullable=False)                # IANA name or "+05:30"
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    place = Column(String(200), default="")
    notes = Column(Text, default="")
    settings = Column(JSON, default=dict)
    created = Column(DateTime, default=datetime.utcnow)
    events = relationship("EventRec", cascade="all, delete-orphan", back_populates="chart")


class EventRec(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    chart_id = Column(Integer, ForeignKey("charts.id"), nullable=False)
    matter_key = Column(String(40), nullable=False)
    date = Column(String(10), nullable=False)
    note = Column(String(300), default="")
    chart = relationship("ChartRec", back_populates="events")


def init():
    Base.metadata.create_all(engine)
