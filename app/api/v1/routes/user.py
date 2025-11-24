from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db, get_db_txonly
from app.schemas.user import JsonFullUserResponse, JsonMultiUserResponse, JsonUserResponse, UserCreate, UserUpdate
from app.services import user as user_service
from app.api.deps import get_current_user
from app.models.user import User
from app.utils.logger import log_api
from app.utils.helpers import convert_pydantic_list_to_tuple, end_route, init_route
from app.schemas.response import NoDataResponse
from app.core.constants import RES_CODE

ACT = "user"
router = APIRouter(prefix="/user", tags=[ACT])


@router.get("/me", 
	response_model=JsonUserResponse | NoDataResponse,
	summary="Get current user profile",
	description="Get the profile information of the currently authenticated user.",
	tags=["get"],
	name="get_me",
	response_description="Current user profile information"
)
async def get_me(response: Response, _: Request, current_user: User = Depends(get_current_user)
):
	"""
	Get the current authenticated user's profile.
	
	Args:
		current_user (User): The current authenticated user.
		
	Returns:
		UserResponse: Current user profile information.
	"""
	msg,rid,code,rescode = "OK",100,RES_CODE.USER,status.HTTP_200_OK
	code = code+RES_CODE.OK_CODE+rid
	log_api(f"Calling routes::user::get_me", level="INFO")
	response.status_code = rescode
	return JsonUserResponse(
		# tx=tx_id,
		# stat=True,
		msg=msg,
		code=code,
		dt=current_user
	)


@router.get("s/", 
	response_model=JsonMultiUserResponse | NoDataResponse,
	summary="Get users",
	description="Get users",
	tags=["get"],
	name="get_users",
	response_description="List of users"
)
async def get_users(response: Response, _: User = Depends(get_current_user)
	, db: Session = Depends(get_db)):
	msg,rid,code,rescode = "OK",200,RES_CODE.USER,status.HTTP_200_OK
	users = None
	field_map = None
	data_rows = None
	log_api(f"Calling routes::user::get_users", level="INFO")
	try:
		users = user_service.get_users(db)
		if users is not None:
			# Exclude sensitive fields from the response
			exclude_fields = ['created_by', 'updated_by', 'updated_at']
			field_map, data_rows = convert_pydantic_list_to_tuple(users, exclude_fields=exclude_fields, sort_fields=True)
			# print("GET USERS", field_map, data_rows)
			code = code+RES_CODE.OK_CODE+rid
			log_api(f"List of users found [{code}]", level="DEBUG")
		else:
			code = code+rid+1
			msg = "Failed to get list of users"
			rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
			log_api(f"Failed to get list of users [{code}]: {msg}", level="ERROR")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid
		msg = str(e)
		log_api(f"Failed to get list of users [{code}]: {e}", level="ERROR")
	
	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonMultiUserResponse(
			stat=True,
			msg=msg,
			code=code,
			dtmap=field_map,
			dt=data_rows
		)


@router.get("/{user_id}", 
	response_model=JsonFullUserResponse,
	summary="Get user by ID",
	description="Get user information by user ID. Requires authentication.",
	tags=["get"],
	name="get_user",
	response_description="User information"
)
async def get_user(response: Response, user_id: int
, _: User = Depends(get_current_user), db: Session = Depends(get_db),
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
	msg,rid,code,rescode = "OK",300,RES_CODE.USER,status.HTTP_200_OK
	db_user = None
	log_api(f"Calling routes::user::get_user", level="INFO")

	try:
		if not user_id or type(user_id) != int:
			rescode = status.HTTP_400_BAD_REQUEST
			code = code+rid+1
			msg = "User ID is required"
			log_api(f"User ID is required [{code}]: {msg}", level="ERROR")


		db_user = user_service.get_user(db, user_id)
		if not db_user:
			code = code+rid+2
			msg = "User not found"
			rescode = status.HTTP_404_NOT_FOUND
			log_api(f"User not found [{code}]: {msg}", level="ERROR")
		else:
			code = code+RES_CODE.OK_CODE+rid
			log_api(f"User found [{code}]: {db_user.username}", level="DEBUG")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid
		msg = str(e)
		log_api(f"Failed to get user [{code}]: {e}", level="ERROR")

	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonFullUserResponse(
			stat=True,
			msg=msg,
			code=code,
			dt=db_user
		)


@router.post("/", 
	response_model=JsonUserResponse | NoDataResponse,
	summary="Create a new user",
	description="Create a new user account. Requires authentication.",
	tags=["post"],
	name="create_user",
	response_description="Created user information"
)
async def create_user(response: Response, 
	user: UserCreate, current_user: User = Depends(get_current_user), 
	db_write: Session = Depends(get_db_txonly), db_read: Session = Depends(get_db),
):
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
	msg,rid,code,rescode = "OK",400,RES_CODE.USER,status.HTTP_200_OK
	db_user = None
	log_api(f"Calling routes::user::create_user", level="INFO")

	try:
		_data = UserCreate.model_validate(user)
		db_user = user_service.create_user(db_write, db_read, _data, current_user)
		if not db_user:
			rescode = status.HTTP_400_BAD_REQUEST
			code = code+rid+1
			msg = "User creation failed"
			log_api(f"User creation failed [{code}]: {msg}", level="ERROR")
		else:
			code = code+RES_CODE.OK_CODE+rid
			rescode = status.HTTP_201_CREATED
			log_api(f"User created successfully [{code}]: {db_user.username}", level="INFO")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid
		msg = str(e)
		log_api(f"Failed to create user [{code}]: {e}", level="ERROR")

	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			# tx=tx_id,
			# req=request.state.req_id,
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonUserResponse(
			# tx=tx_id,
			# req=request.state.req_id,
			stat=True,
			msg=msg,
			code=code,
			dt=db_user
		)


@router.put("/{user_id}", 
	response_model=JsonUserResponse | NoDataResponse,
	summary="Update user",
	description="Update user information by user ID. Requires authentication.",
	tags=["put"],
	name="update_user",
	response_description="Updated user information"
)
async def update_user(response: Response, 
	user_id: int, user: UserUpdate, db_read: Session = Depends(get_db),
	db_write: Session = Depends(get_db_txonly),
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
	msg,rid,code,rescode = "OK",500,RES_CODE.USER,status.HTTP_200_OK
	db_user2 = None
	log_api(f"Calling routes::user::update_user", level="INFO")
	try:
		if not user_id or type(user_id) != int:
			code = code+rid+1
			msg = "User ID is required"
			log_api(f"User ID is required [{code}]: {msg}", level="ERROR")
			rescode = status.HTTP_400_BAD_REQUEST
		else:
			db_user = user_service.get_user(db_read, user_id)
			if not db_user:
				code = code+rid+2
				msg = "User not found"
				rescode = status.HTTP_404_NOT_FOUND
				log_api(f"User not found [{code}]: {msg}", level="ERROR")
			else:
				_data = UserUpdate.model_validate(user)
				db_user2 = user_service.update_user(db_write, db_read, db_user, _data, current_user)
				if not db_user2:
					rescode = status.HTTP_400_BAD_REQUEST
					code = code+rid+3
					msg = "User update failed"
					log_api(f"User update failed [{code}]: {msg}", level="ERROR")
				else:
					code = code+RES_CODE.OK_CODE+rid
					log_api(f"User updated successfully [{code}]: {db_user2.username}", level="INFO")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid
		msg = str(e)
		log_api(f"Failed to update user [{code}]: {e}", level="ERROR")

	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonUserResponse(
			stat=True,
			msg=msg,
			code=code,
			dt=db_user2
		)


@router.delete("/{user_id}", 
	response_model=JsonUserResponse | NoDataResponse,
	summary="Delete user",
	description="Delete user by user ID. Requires authentication.",
	tags=["delete"],
	name="delete_user",
	response_description="Deletion confirmation message"
)
async def delete_user(response: Response, 
	user_id: int, _: User = Depends(get_current_user), db_read: Session = Depends(get_db),
	db_write: Session = Depends(get_db_txonly),
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
	msg,rid,code,rescode = "OK",600,RES_CODE.USER,status.HTTP_200_OK
	db_user = None
	log_api(f"Calling routes::user::delete_user", level="INFO")
	try:
		if not user_id or type(user_id) != int:
			code = code+rid+1
			msg = "User ID is required"
			log_api(f"User ID is required [{code}]: {msg}", level="ERROR")
			rescode = status.HTTP_400_BAD_REQUEST
		else:
			db_user = user_service.get_user(db_read, user_id)
			if not db_user:
				code = code+rid+2
				msg = "User not found"
				rescode = status.HTTP_404_NOT_FOUND
				log_api(f"User not found [{code}]: {msg}", level="ERROR")
			else:
				success = user_service.delete_user(db_write, user_id)
				if not success:
					code = code+rid+3
					msg = "User delete failed"
					rescode = status.HTTP_404_NOT_FOUND
					log_api(f"User delete failed [{code}]: {msg}", level="ERROR")
				else:
					code = code+RES_CODE.OK_CODE+rid
					log_api(f"User deleted successfully [{code}]: {user_id}", level="INFO")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid	
		msg = str(e)
		log_api(f"Failed to delete user [{code}]: {e}", level="ERROR")

	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonUserResponse(
			stat=True,
			msg=msg,
			code=code,
			dt=db_user
		)
