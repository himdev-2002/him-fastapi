
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Item(Base):
	__tablename__ = "items"
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String, nullable=False)
	description = Column(String, nullable=True)
	owner_id = Column(Integer, nullable=False)
