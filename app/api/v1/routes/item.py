
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import schemas
from app.services import item_service

ACT = "item"
router = APIRouter(prefix="/item", tags=[ACT])

@router.post("/", response_model=schemas.item.ItemResponse)
def create_item(item: schemas.item.ItemCreate, db: Session = Depends(get_db)):
	return item_service.create_item(db, item)

@router.get("/{item_id}", response_model=schemas.item.ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
	db_item = item_service.get_item(db, item_id)
	if not db_item:
		raise HTTPException(status_code=404, detail="Item not found")
	return db_item

@router.put("/{item_id}", response_model=schemas.item.ItemResponse)
def update_item(item_id: int, item: schemas.item.ItemUpdate, db: Session = Depends(get_db)):
	db_item = item_service.update_item(db, item_id, item)
	if not db_item:
		raise HTTPException(status_code=404, detail="Item not found")
	return db_item

@router.delete("/{item_id}", response_model=schemas.response.MessageResponse)
def delete_item(item_id: int, db: Session = Depends(get_db)):
	success = item_service.delete_item(db, item_id)
	if not success:
		raise HTTPException(status_code=404, detail="Item not found")
	return {"message": "Item deleted successfully"}
