
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Item(Base):
	__tablename__ = "m_items"
	__table_args__ = {'info': {'skip_autogenerate': True}}

	# Primary key field - unique identifier for each user record
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String, nullable=False)
	description = Column(String, nullable=True)
	owner_id = Column(Integer, nullable=False)
