from datetime import datetime
from enum import Enum
from sqlalchemy import CheckConstraint, Column, Integer, DateTime, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ApiPermission(Base):
    # Database table name for this model
    __tablename__ = "r_api_permission"
    
    # Primary key field - unique identifier for each user record
    id = Column(Integer, primary_key=True, index=True)

    api_id = Column(Integer, ForeignKey('m_apis.id'), index=True)

    profile_id = Column(Integer, ForeignKey('m_profiles.id'), index=True)

    # Active status flag - determines if user can login (default: True)
    is_active = Column(Boolean, default=True)
    
    # Audit field - ID of user who created this account (nullable, default: 0)
    created_by = Column(Integer, nullable=True, default=0)
    
    # Audit field - timestamp when account was created (auto-set on creation)
    created_at = Column(DateTime, default=datetime.now)
    
    # Audit field - ID of user who last updated this account (nullable, default: 0)
    updated_by = Column(Integer, nullable=True, default=0)
    
    # Audit field - timestamp when account was last updated (auto-set on update)
    updated_at = Column(DateTime, default=datetime.now)

    api = relationship('Api', back_populates='profile') # many to one

    profile = relationship('Profile', back_populates='api_perms') # many to many
    
    __table_args__ = (
        UniqueConstraint('api_id', 'profile_id', name='api_permission_uniq_1'),
    )

    def __repr__(self):
        return f"<ApiPermission(id={self.id}, api_id={self.api_id}, profile_id={self.profile_id})>"