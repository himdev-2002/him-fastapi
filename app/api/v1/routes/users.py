
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.middlewares.context import set_route, set_tx_id, reset_tx_id, reset_route
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import JsonFullUserResponse, JsonUserResponse, UserResponse, UserCreate, UserUpdate, FullUserResponse
from app.services import user_service
from app.api.deps import get_current_user, get_current_active_user
from app.models.user import User
from app.utils.logger import log_api
from app.utils.helpers import end_route, get_current_route, init_route
from app.schemas.response import MessageResponse
from app.core.constants import RES_CODE

router = APIRouter(prefix="/users", tags=["user"])

@router.post(
	"/", 
	response_model=UserResponse,
	summary="Create a new user",
	description="Create a new user account. This endpoint is public and does not require authentication.",
	tags=["user"],
	response_description="Created user information"
)
async def create_user(request: Request, user: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
	tx_id = generate_tx_id(act="add_user")
	route = get_current_route(request)
	log_api("Creating new user",route=route['path'], user=str(current_user.id), act="add_user", level="INFO", tx_id=tx_id)
	setattr(request.state, "user", user.username)
	setattr(request.state, "tx_id", tx_id)
	setattr(request.state, "act", "add_user")
	tx_token = await set_tx_id(tx_id)
	route_token = await set_route(route['path'])
	db_user = user_service.create_user(db, user, current_user)
	if not db_user:
		await reset_tx_id(tx_token)
		await reset_route(route_token)
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
			detail="User creation failed"
		)
	log_api("User created successfully", user=str(current_user.id), act="add_user", level="INFO", tx_id=tx_id, route=route['path'])
	return db_user


@router.get(
	"/me", 
	response_model=JsonUserResponse,
	summary="Get current user profile",
	description="Get the profile information of the currently authenticated user.",
	tags=["user"],
	response_description="Current user profile information"
)
async def get_current_user_profile(request: Request, current_user: User = Depends(get_current_user)):
	"""
	Get the current authenticated user's profile.
	
	Args:
		current_user (User): The current authenticated user.
		
	Returns:
		UserResponse: Current user profile information.
	"""
	tx_id, route, tx_token, route_token = await init_route(request, current_user.username, "user", "current_user")
	log_api(f"Getting profile for user: {current_user.username}", user=str(current_user.id), act="user", level="INFO", tx_id=tx_id, route=route['path'])
	await end_route(tx_token, route_token)
	return JsonUserResponse(
		tx=tx_id,
		stat=True,
		msg="OK",
		code=RES_CODE.USER+RES_CODE.OK_CODE+1,
		dt=current_user
	)


@router.get(
	"/{user_id}", 
	response_model=JsonFullUserResponse,
	summary="Get user by ID",
	description="Get user information by user ID. Requires authentication.",
	tags=["user"],
	response_description="User information"
)
async def read_user(
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
	tx_token = await set_tx_id(tx_id)
	route_token = await set_route(route['path'])
	log_api(f"Getting user {user_id} by user {current_user.username}", user=str(current_user.id), act="read_user", level="INFO", tx_id=tx_id, route=route['path'])
	db_user = user_service.get_user(db, user_id)
	if not db_user:
		await reset_tx_id(tx_token)
		await reset_route(route_token)
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
			detail="User not found"
		)
	await reset_tx_id(tx_token)
	await reset_route(route_token)
	return JsonFullUserResponse(
		stat=True,
		msg="OK",
		dt=db_user
	)


@router.put(
	"/{user_id}", 
	response_model=JsonUserResponse,
	summary="Update user",
	description="Update user information by user ID. Requires authentication.",
	tags=["user"],
	response_description="Updated user information"
)
def update_user(
	request: Request,
	user_id: int, 
	user: UserUpdate, 
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
	log_api(f"Updating user {user_id} by user {current_user.username}", user=str(current_user.id), act="update_user", level="INFO")
	tx_id = generate_tx_id(act="update_user")
	route = get_current_route(request)
	setattr(request.state, "user", current_user.username)
	setattr(request.state, "tx_id", tx_id)
	setattr(request.state, "act", "update_user")
	log_api(f"Updating user {user_id} by user {current_user.username}", user=str(current_user.id), act="update_user", level="INFO", tx_id=tx_id, route=route['path'])
	db_user = user_service.update_user(db, user_id, user)
	if not db_user:
		return JsonUserResponse(
			stat=False,
			msg="NOK",
			dt=None
		)
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, 
			detail="User not found"
		)
	return JsonUserResponse(
		stat=True,
		msg="OK",
		dt=db_user
	)


@router.delete(
	"/{user_id}", 
	response_model=MessageResponse,
	summary="Delete user",
	description="Delete user by user ID. Requires authentication.",
	tags=["user"],
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
