from datetime import datetime
from enum import Enum
from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, Boolean, Enum as SQLAlchemyEnum, UniqueConstraint
from app.core.database import Base
from sqlalchemy.orm import relationship

class HTTPMethodEnum(str, Enum):  # <- penting: turunan dari str & Enum
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    ALL = "ALL"

class Api(Base):
    # Database table name for this model
    __tablename__ = "m_apis"
    
    # Primary key field - unique identifier for each user record
    id = Column(Integer, primary_key=True, index=True)

    method = Column(SQLAlchemyEnum(HTTPMethodEnum), nullable=False, index=True)
    
    version = Column(Integer, nullable=False, default=1, index=True)

    act = Column(String, nullable=False, index=True)

    name = Column(String, nullable=False)

    path = Column(String, nullable=True)

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

    profile_api_perms = relationship('ApiPermission', back_populates='api', cascade='none')
    profile = relationship('Profile', secondary='r_api_permission', back_populates='api_perms') # many to one

    __table_args__ = (
        UniqueConstraint('method', 'version', 'act', 'name', name='api_uniq_1'),
        CheckConstraint('version > 0', name='api_chk_1'),
    )

    def __repr__(self):
        return f"<Api(id={self.id}, method={self.method}, version={self.version}, act={self.act}, name={self.name}, path={self.path})>"