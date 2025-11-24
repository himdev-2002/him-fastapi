from datetime import datetime
from enum import Enum
from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, Integer, String, DateTime, Boolean, Enum as SQLAlchemyEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class FileStore(str, Enum):
    """Storage backend type enumeration."""
    RUSTFS = "rustfs"
    MINIO = "minio"

class FileMeta(Base):
    __tablename__ = "m_file_meta"
    
    id = Column(Integer, primary_key=True, index=True)
    
    file_type = Column(String, nullable=False, index=True)
    
    name = Column(String, nullable=False)
    
    size = Column(BigInteger, nullable=False)

    store_type = Column(SQLAlchemyEnum(FileStore), default=FileStore.RUSTFS, nullable=False, index=True)
    
    content_type = Column(String, nullable=False)

    rustfs_key = Column(String, unique=True)

    minio_key = Column(String, unique=True)
    
    uploaded_at = Column(DateTime, default=datetime.now)
    
    uploaded_by = Column(Integer, ForeignKey('m_users.id'), index=True)

    __table_args__ = (
        UniqueConstraint('store_type','rustfs_key', name='file_meta_uniq_1'),
        UniqueConstraint('store_type', 'minio_key', name='file_meta_uniq_2'),
    )

    def __repr__(self):
        """String representation of FileMeta instance."""
        return f"<FileMeta(id={self.id}, file_type='{self.file_type}', name='{self.name}', store_type='{self.store_type.value}', content_type='{self.content_type}')>"