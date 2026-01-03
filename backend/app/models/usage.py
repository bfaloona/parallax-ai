"""Usage tracking models for token consumption."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class UsageRecord(Base):
    """Individual API call usage record."""

    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), nullable=False)
    model = Column(String(50), nullable=False)  # haiku, sonnet, opus
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_records")

    # Indexes for efficient queries
    __table_args__ = (
        Index("ix_usage_user_created", "user_id", "created_at"),
        Index("ix_usage_conversation", "conversation_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<UsageRecord(id={self.id}, user_id={self.user_id}, "
            f"model={self.model}, input={self.input_tokens}, output={self.output_tokens})>"
        )


class MonthlyUsage(Base):
    """Aggregated monthly usage per user and model."""

    __tablename__ = "monthly_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    model = Column(String(50), nullable=False)  # haiku, sonnet, opus
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="monthly_usage")

    # Composite unique constraint - one row per user/year/month/model
    __table_args__ = (
        Index("ix_monthly_usage_unique", "user_id", "year", "month", "model", unique=True),
        Index("ix_monthly_usage_period", "year", "month"),
    )

    def __repr__(self) -> str:
        return (
            f"<MonthlyUsage(user_id={self.user_id}, {self.year}-{self.month:02d}, "
            f"model={self.model}, tokens={self.total_input_tokens}+{self.total_output_tokens})>"
        )
