
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import schemas
from app.services import user_service
from app.api.deps import get_current_user, get_current_active_user
from app.models.user import User
from app.utils.logger import log_api
from app.utils.helpers import generate_tx_id, get_current_route

router = APIRouter(prefix="/users", tags=["user"])

@router.post(
	"/", 
	response_model=schemas.user.UserResponse,
	summary="Create a new user",
	description="Create a new user account. This endpoint is public and does not require authentication.",
	tags=["User Management"],
	response_description="Created user information"
)
def create_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
	"""
	Create a new user account.
	
	Args:
		user (UserCreate): User creation data.
		db (Session): Database session.
		
	Returns:
		UserResponse: Created user information.
		
	Raises:
		HTTPException: If user creation fails.
	"""
	log_api("Creating new user", act="user", level="INFO")
	return user_service.create_user(db, user)


@router.get(
	"/me", 
	response_model=schemas.user.UserResponse,
	summary="Get current user profile",
	description="Get the profile information of the currently authenticated user.",
	tags=["User Management"],
	response_description="Current user profile information"
)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
	"""
	Get the current authenticated user's profile.
	
	Args:
		current_user (User): The current authenticated user.
		
	Returns:
		UserResponse: Current user profile information.
	"""
	log_api(f"Getting profile for user: {current_user.username}", user=str(current_user.id), act="user", level="INFO")
	return current_user


@router.get(
	"/{user_id}", 
	response_model=schemas.user.UserResponse,
	summary="Get user by ID",
	description="Get user information by user ID. Requires authentication.",
	tags=["User Management"],
	response_description="User information"
)
def read_user(
	request: Request, 
	user_id: int, 
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Get user information by ID.
	
	Args:
		user_id (int): The user ID to retrieve.
		current_user (User): The current authenticated user.
		
	Returns:
		UserResponse: User information.
		
	Raises:
		HTTPException: If user is not found.
	"""
	log_api(f"Getting user {user_id} by user {current_user.username}", user=str(current_user.id), act="read_user", level="INFO")
	tx_id = generate_tx_id(act="read_user")
	route = get_current_route(request)
	setattr(request.state, "user", current_user.username)
	setattr(request.state, "tx_id", tx_id)
	setattr(request.state, "act", "read_user")
	log_api(f"Getting user {user_id} by user {current_user.username}", user=str(current_user.id), act="read_user", level="INFO", tx_id=tx_id, route=route['path'])
	db_user = user_service.get_user(db, user_id)
	if not db_user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, 
			detail="User not found"
		)
	return db_user


@router.put(
	"/{user_id}", 
	response_model=schemas.user.UserResponse,
	summary="Update user",
	description="Update user information by user ID. Requires authentication.",
	tags=["User Management"],
	response_description="Updated user information"
)
def update_user(
	user_id: int, 
	user: schemas.user.UserUpdate, 
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Update user information.
	
	Args:
		user_id (int): The user ID to update.
		user (UserUpdate): Updated user data.
		db (Session): Database session.
		current_user (User): The current authenticated user.
		
	Returns:
		UserResponse: Updated user information.
		
	Raises:
		HTTPException: If user is not found.
	"""
	log_api(f"Updating user {user_id} by user {current_user.username}", user=str(current_user.id), act="user", level="INFO")
	db_user = user_service.update_user(db, user_id, user)
	if not db_user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, 
			detail="User not found"
		)
	return db_user


@router.delete(
	"/{user_id}", 
	response_model=schemas.response.MessageResponse,
	summary="Delete user",
	description="Delete user by user ID. Requires authentication.",
	tags=["User Management"],
	response_description="Deletion confirmation message"
)
def delete_user(
	user_id: int, 
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""
	Delete user by ID.
	
	Args:
		user_id (int): The user ID to delete.
		db (Session): Database session.
		current_user (User): The current authenticated user.
		
	Returns:
		MessageResponse: Deletion confirmation message.
		
	Raises:
		HTTPException: If user is not found.
	"""
	log_api(f"Deleting user {user_id} by user {current_user.username}", user=str(current_user.id), act="user", level="INFO")
	success = user_service.delete_user(db, user_id)
	if not success:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, 
			detail="User not found"
		)
	return {"message": "User deleted successfully"}
