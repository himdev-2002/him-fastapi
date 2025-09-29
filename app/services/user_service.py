from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User

from app.schemas.user import UserCreate, UserUpdate, UserLoginResponse
from app.core.database import engine_sync
from app.utils.database import get_raw_sql, map_to_pydantic
from sqlalchemy import select

from app.utils.logger import log_api
from app.utils.helpers import verify_password, hash_password
from app.middlewares.context import get_tx_id, get_route

def authenticate_user(username: str, password: str):
	# print("Authenticating user:", username)
	tx_id = get_tx_id()
	route = get_route()
	log_api(f"Authenticating user: {username}", user=username, route=route, act="auth", level="INFO", tx_id=tx_id)
	query = select(User).where(User.username == username)
	try:
		with engine_sync.connect() as conn:
			# print(get_raw_sql(query, conn))
			result = conn.execute(query)
			res_data = result.first()
			user = map_to_pydantic(res_data, UserLoginResponse) if res_data else None
			# print(user)
			if not user:
				log_api(f"User not found", user=username, route=route, act="auth", level="ERROR", tx_id=tx_id)
				return None

			if user.is_active is False or user.is_active is None:
				log_api(f"User is not active", user=username, route=route, act="auth", level="ERROR", tx_id=tx_id)
				return None
			
			# TODO: hash password for comparison
			if not verify_password(password, user.password):
				log_api(f"Invalid password", user=username, route=route, act="auth", level="ERROR", tx_id=tx_id)
				return None
			log_api(f"User authenticated successfully", user=str(user.id), route=route, act="auth", level="INFO", tx_id=tx_id)
			return user
	except Exception as e:
		log_api(f"Error during authentication: {e}", user=username, route=route, act="auth", level="ERROR", tx_id=tx_id)
		return None

def create_user(db: Session, user: UserCreate, current_user: User):
	tx_id = get_tx_id()
	route = get_route()
	log_api(f"Creating new user: {user}", user=str(current_user.id), route=route, act="add_user", level="INFO", tx_id=tx_id)
	
	try:
		hashed_password = hash_password(user.password)
		new_user = User(
			username=user.username,
			email=user.email,
			password=hashed_password,
			is_active=user.is_active,
			created_by=current_user.id,
			created_at=datetime.now(),
			updated_by=current_user.id,
			updated_at=datetime.now()
		)
		log_api(f"New user: {new_user}", user=str(current_user.id), route=route, act="add_user", level="INFO", tx_id=tx_id)
		db.add(new_user)
		db.commit()
		db.refresh(new_user)
		log_api(f"User created successfully", user=str(current_user.id), route=route, act="add_user", level="INFO", tx_id=tx_id)
		return new_user
	except Exception as e:
		log_api(f"Error during user creation: {e}", user=str(current_user.id), route=route, act="add_user", level="ERROR", tx_id=tx_id)
		return None

def get_user(db: Session, user_id: int):
	tx_id = get_tx_id()
	route = get_route()
	log_api(f"Getting user: {user_id}", user=str(user_id), route=route, act="get_user", level="INFO", tx_id=tx_id)
	try:
		user = db.query(User).filter(User.id == user_id).first()
		if user:
			log_api(f"User found", user=str(user.id), route=route, act="get_user", level="INFO", tx_id=tx_id)
			return user
		else:
			log_api(f"User not found", user=str(user_id), route=route, act="get_user", level="ERROR", tx_id=tx_id)
			return None
	except Exception as e:
		log_api(f"Error during user retrieval: {e}", user=str(user_id), route=route, act="get_user", level="ERROR", tx_id=tx_id)
		return None

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
