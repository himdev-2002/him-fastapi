
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
	__tablename__ = "m_users"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	password = Column(String, nullable=False)
