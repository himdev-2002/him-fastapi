
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def create_user(db: Session, user: UserCreate):
	new_user = User(
		name=user.name,
		email=user.email,
		password=user.password  # TODO: hash password
	)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return new_user

def get_user(db: Session, user_id: int):
	return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: UserUpdate):
	user = db.query(User).filter(User.id == user_id).first()
	if user:
		user.name = user_update.name
		user.email = user_update.email
		db.commit()
		db.refresh(user)
	return user

def delete_user(db: Session, user_id: int):
	user = db.query(User).filter(User.id == user_id).first()
	if user:
		db.delete(user)
		db.commit()
		return True
	return False
