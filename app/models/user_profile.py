from datetime import datetime
from enum import Enum
from sqlalchemy import CheckConstraint, Column, Integer, DateTime, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserProfile(Base):
    # Database table name for this model
    __tablename__ = "r_user_profile"
    
    # Primary key field - unique identifier for each user record
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey('m_users.id'), index=True)

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

    user = relationship('User', back_populates='profiles') # many to many

    profile = relationship('Profile', back_populates='users') # many to many
    
    __table_args__ = (
        UniqueConstraint('user_id', 'profile_id', name='user_profile_uniq_1'),
    )

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, profile_id={self.profile_id})>"