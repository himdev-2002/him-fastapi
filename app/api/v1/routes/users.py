
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import schemas
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.user.UserResponse)
def create_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
	return user_service.create_user(db, user)

@router.get("/{user_id}", response_model=schemas.user.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
	db_user = user_service.get_user(db, user_id)
	if not db_user:
		raise HTTPException(status_code=404, detail="User not found")
	return db_user

@router.put("/{user_id}", response_model=schemas.user.UserResponse)
def update_user(user_id: int, user: schemas.user.UserUpdate, db: Session = Depends(get_db)):
	db_user = user_service.update_user(db, user_id, user)
	if not db_user:
		raise HTTPException(status_code=404, detail="User not found")
	return db_user

@router.delete("/{user_id}", response_model=schemas.response.MessageResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
	success = user_service.delete_user(db, user_id)
	if not success:
		raise HTTPException(status_code=404, detail="User not found")
	return {"message": "User deleted successfully"}
