from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User

from app.schemas.user import UserCreate, UserUpdate, UserLoginResponse, PublicFullUserResponse
from app.core.database import engine_sync
from app.utils.database import get_raw_sql, map_to_pydantic
from sqlalchemy import delete, insert, select, update

from app.utils.logger import log_api
from app.utils.helpers import model_to_dict, verify_password, hash_password

def authenticate_user(username: str, password: str):
	# print("Authenticating user:", username)
	log_api(f"Calling services::user::authenticate_user", level="INFO")
	query = select(User).where(User.username == username)
	try:
		with engine_sync.connect() as conn:
			# print(get_raw_sql(query, conn))
			result = conn.execute(query)
			res_data = result.first()
			user = map_to_pydantic(res_data, UserLoginResponse) if res_data else None
			# print(user)
			if not user:
				log_api(f"User not found", user=username, level="INFO")
				return None

			if user.is_active is False or user.is_active is None:
				log_api(f"User is not active", user=username, level="INFO")
				return None
			
			# TODO: hash password for comparison
			if not verify_password(password, user.password):
				log_api(f"Invalid password", user=username, level="INFO")
				return None
			log_api(f"User authenticated successfully", user=str(user.id), level="DEBUG")
			return user
	except Exception as e:
		log_api(f"Error during authentication: {e}", user=username, level="ERROR")
		return None


def create_user(db_write: Session, db_read: Session, user: UserCreate, current_user: User):
	log_api(f"Calling services::user::create_user", level="INFO")
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
		# db.add(new_user)
		# print("CREATE USER: ",model_to_dict(new_user,exclude=["id"]))
		stmt = insert(User).values(model_to_dict(new_user,exclude=["id"])).returning(None)
		db_write.execute(stmt)
		db_write.flush()
		# db_write.add(new_user)
		db_write.commit()
		new_user = get_user_by_username(db_read, user.username)
		# db_read.refresh(new_user)
		return new_user
	except Exception as e:
		log_api(f"Error during user creation: {e}",level="ERROR")
		return None


def update_user(db_write: Session, db_read: Session, user: User, user_update: UserUpdate, current_user: User):
	# user = db.query(User).filter(User.id == user_id).first()
	log_api(f"Calling services::user::update_user", level="INFO")
	try:
		if user:
			user.username = user_update.username
			user.email = user_update.email
			user.is_active = user_update.is_active
			user.updated_by = current_user.id
			user.updated_at = datetime.now()

			stmt = update(User).where(User.id == user.id).values(model_to_dict(user,exclude=["id"])).returning(None)
			db_write.execute(stmt)
			db_write.flush()
			db_write.commit()
			user = get_user_by_username(db_read, user.username)
		return user
	except Exception as e:
		log_api(f"Error during user update: {e}", level="ERROR")
		return None


def delete_user(db_write: Session, user_id: int):
	log_api(f"Calling services::user::delete_user", level="INFO")
	try:
		stmt = delete(User).where(User.id == user_id).returning(None)
		db_write.execute(stmt)
		db_write.flush()
		db_write.commit()
		return True
	except Exception as e:
		log_api(f"Error during user deletion: {e}", level="ERROR")
		return False


def get_user(db: Session, user_id: int):
	log_api(f"Calling services::user::get_user", level="DEBUG")
	try:
		user = db.query(User).filter(User.id == user_id).first()
		if user:
			log_api(f"User found", level="DEBUG")
			return user
		else:
			log_api(f"User not found", level="ERROR")
			return None
	except Exception as e:
		log_api(f"Error during user retrieval: {e}", level="ERROR")
		return None


def get_user_by_username(db: Session, username: str):
	log_api(f"Calling services::user::get_user_by_username", level="DEBUG")
	try:
		user = db.query(User).filter(User.username == username).first()
		if user:
			log_api(f"User found", level="DEBUG")
			return user
		else:
			log_api(f"User not found", level="ERROR")
			return None
	except Exception as e:
		log_api(f"Error during user retrieval: {e}", level="ERROR")
		return None


def get_users(db: Session):
	log_api(f"Calling services::user::get_users", level="INFO")
	try:
		users = db.query(User).all()
		return map_to_pydantic(users, PublicFullUserResponse)
	except Exception as e:
		log_api(f"Error during call services::user::get_users: {e}", level="ERROR")
		return None

