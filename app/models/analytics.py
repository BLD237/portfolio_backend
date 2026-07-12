from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    referrer: Mapped[str] = mapped_column(String(255), default="Direct")
    user_agent: Mapped[str] = mapped_column(String(500), default="")
    device_type: Mapped[str] = mapped_column(String(50), default="Desktop")
    os: Mapped[str] = mapped_column(String(50), default="Unknown")
    browser: Mapped[str] = mapped_column(String(50), default="Unknown")
    location: Mapped[str] = mapped_column(String(100), default="Unknown")
    isp: Mapped[str] = mapped_column(String(100), default="Unknown")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
