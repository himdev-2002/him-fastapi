
"""
User Model

Defines the User entity for the database with comprehensive user management fields.
This model represents user accounts in the system with authentication and audit capabilities.

Fields:
    id: Primary key identifier
    username: Unique username for login
    email: Unique email address for user identification
    password: Hashed password for authentication
    is_active: Account status flag
    created_by: ID of user who created this account
    created_at: Timestamp when account was created
    updated_by: ID of user who last updated this account
    updated_at: Timestamp when account was last updated

Database Table: m_users
"""

from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    User model representing user accounts in the system.
    
    This model defines the structure for user authentication and management,
    including audit fields for tracking creation and modification history.
    
    Attributes:
        id (int): Primary key, auto-incrementing user identifier
        username (str): Unique username for login authentication
        email (str): Unique email address for user identification and communication
        password (str): Hashed password for secure authentication
        is_active (bool): Account status flag indicating if user can login
        created_by (int): ID of the user who created this account (audit field)
        created_at (datetime): Timestamp when the account was created
        updated_by (int): ID of the user who last updated this account (audit field)
        updated_at (datetime): Timestamp when the account was last modified
    
    Example:
        user = User(
            username="john_doe",
            email="john@example.com",
            password="hashed_password",
            is_active=True
        )
    """
    
    # Database table name for this model
    __tablename__ = "m_users"
    
    # Primary key field - unique identifier for each user record
    id = Column(Integer, primary_key=True, index=True)
    
    # Username field - must be unique and required for login
    username = Column(String, nullable=False)
    
    # Email field - unique identifier, indexed for fast lookups, required
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Password field - stores hashed password, required for authentication
    password = Column(String, nullable=False)
    
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

    user_profiles = relationship('UserProfile', back_populates='user', cascade='none')
    profiles = relationship('Profile', secondary='r_user_profile', back_populates='user', cascade='none')

    __table_args__ = (
        UniqueConstraint('username', name='user_uniq_1'),
        UniqueConstraint('email', name='user_uniq_2')
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"