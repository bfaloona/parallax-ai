"""User model with authentication support."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import bcrypt

from app.models.base import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    tier = Column(String(20), default="free")  # free, starter, pro, enterprise
    tier_updated_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    monthly_usage = relationship("MonthlyUsage", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Hash and set user password using bcrypt.

        Args:
            password: Plain text password to hash
        """
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        # Bcrypt has a 72-byte limit, truncate if necessary (must match set_password)
        password_bytes = password.encode('utf-8')[:72]
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, tier={self.tier})>"
