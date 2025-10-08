from datetime import datetime
from enum import Enum
from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Profile(Base):
    # Database table name for this model
    __tablename__ = "m_profiles"
    
    # Primary key field - unique identifier for each user record
    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    description = Column(String, nullable=True)

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

    user_profiles = relationship('UserProfile', back_populates='profile', cascade='none')
    user = relationship('User', secondary='r_user_profile', back_populates='profiles') # many to many

    profile_api_perms = relationship('ApiPermission', back_populates='profile', cascade='none')
    api_perms = relationship('Api', secondary='r_api_permission', back_populates='profile', cascade='none') # one to many
    
    __table_args__ = (
        UniqueConstraint('name', name='profile_uniq_1'),
    )

    def __repr__(self):
        return f"<Profile(id={self.id}, name={self.name})>"