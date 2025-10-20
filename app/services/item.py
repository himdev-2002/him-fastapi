
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

def create_item(db: Session, item: ItemCreate):
	new_item = Item(
		title=item.title,
		description=item.description,
		owner_id=item.owner_id
	)
	db.add(new_item)
	db.commit()
	db.refresh(new_item)
	return new_item

def get_item(db: Session, item_id: int):
	return db.query(Item).filter(Item.id == item_id).first()

def update_item(db: Session, item_id: int, item_update: ItemUpdate):
	item = db.query(Item).filter(Item.id == item_id).first()
	if item:
		item.title = item_update.title
		item.description = item_update.description
		db.commit()
		db.refresh(item)
	return item

def delete_item(db: Session, item_id: int):
	item = db.query(Item).filter(Item.id == item_id).first()
	if item:
		db.delete(item)
		db.commit()
		return True
	return False
