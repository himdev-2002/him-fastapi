
from datetime import datetime
import os
from typing import Union
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.schemas.file_meta import FileMetaCreate, FileMetaCreateDB, JsonFileMetaResponse, JsonFullFileMetaResponse, JsonMultiFileMetaResponse
from app.schemas.response import NoDataResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.core.constants import RES_CODE
from app.utils.logger import log_api
from app.core.database import get_db, get_db_txonly
from fastapi import Depends, File, Form, Response, status, UploadFile
from app.services import file_meta as file_meta_service
from app.utils.helpers import convert_pydantic_list_to_tuple
from app.models.file_meta import FileStore
from app.utils.rustfs import remove_file_from_rustfs, upload_file_to_rustfs
from app.core.config import settings


ACT = "file"
router = APIRouter(prefix="/file", tags=[ACT])

@router.get("s/", 
	response_model=JsonMultiFileMetaResponse | NoDataResponse,
	summary="Get files",
	description="Get files",
	tags=["get"],
	name="get_files",
	response_description="List of files"
)
async def get_files(response: Response, _: User = Depends(get_current_user)
	, db: Session = Depends(get_db)):
	msg,rid,code,rescode = "OK",100,RES_CODE.FILE,status.HTTP_200_OK
	file_metas = None
	field_map = None
	data_rows = None
	log_api(f"Calling routes::file::get_files", level="INFO")
	try:
		file_metas = file_meta_service.get_file_metas(db)
		if file_metas is not None:
			# Exclude sensitive fields from the response
			exclude_fields = []
			field_map, data_rows = convert_pydantic_list_to_tuple(file_metas, exclude_fields=exclude_fields, sort_fields=True)
			# print("GET USERS", field_map, data_rows)
			code = code+RES_CODE.OK_CODE+rid
			log_api(f"List of files found [{code}]", level="DEBUG")
		else:
			code = code+rid+1
			msg = "Failed to get list of files"
			rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
			log_api(f"Failed to get list of files [{code}]: {msg}", level="ERROR")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid
		msg = str(e)
		log_api(f"Failed to get list of files [{code}]: {e}", level="ERROR")
	
	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonMultiFileMetaResponse(
			stat=True,
			msg=msg,
			code=code,
			dtmap=field_map,
			dt=data_rows
		)

@router.get("/{file_id}", 
	response_model=JsonFullFileMetaResponse,
	summary="Get file by ID",
	description="Get file information by file ID. Requires authentication.",
	tags=["get"],
	name="get_file",
	response_description="File information"
)
async def get_file(response: Response, file_id: int
, _: User = Depends(get_current_user), db: Session = Depends(get_db),
):
	msg,rid,code,rescode = "OK",200,RES_CODE.FILE,status.HTTP_200_OK
	file_meta = None
	log_api(f"Calling routes::file::get_file", level="INFO")
	try:
		file_meta = file_meta_service.get_file_meta(db, file_id)
		if file_meta is not None:
			code = code+RES_CODE.OK_CODE+rid
			log_api(f"File found [{code}]: {file_meta.name}", level="DEBUG")
		else:
			code = code+rid+1
			msg = "Failed to get file"
			rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
			log_api(f"Failed to get file [{code}]: {msg}", level="ERROR")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid
		msg = str(e)
		log_api(f"Failed to get file [{code}]: {e}", level="ERROR")
	
	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonFullFileMetaResponse(
			stat=True,
			msg=msg,
			code=code,
			dt=file_meta
		)

@router.post("/", 
	response_model=JsonFileMetaResponse | NoDataResponse,
	summary="Upload a new file",
	description="Upload a new file. Requires authentication. Accepts multipart/form-data with file and metadata fields.",
	tags=["post"],
	name="upload_file",
	response_description="Uploaded file information"
)
async def upload_file(
	response: Response,
	file: UploadFile = File(..., description="The file to upload"),
	file_type: Union[str, None] = Form(None, description="Type/category of the file", example="image"),
	name: Union[str, None] = Form(None, description="Original filename (optional, defaults to uploaded filename)", example="photo.jpg"),
	store_type: FileStore = Form(FileStore.RUSTFS, description="Storage backend type", example=FileStore.RUSTFS),
	current_user: User = Depends(get_current_user),
	db_write: Session = Depends(get_db_txonly),
	db_read: Session = Depends(get_db),
):
	"""
	Upload a new file with metadata.
	
	This endpoint accepts multipart/form-data with:
	- file: The file to upload (required)
	- file_type: Optional file type/category
	- name: Optional filename (defaults to uploaded filename)
	- store_type: Storage backend (defaults to rustfs)
	
	Args:
		file: The uploaded file
		file_type: Optional file type/category
		name: Optional filename
		store_type: Storage backend type
		current_user: Authenticated user (injected via dependency)
		db_write: Database session for write operations
		db_read: Database session for read operations
		
	Returns:
		JsonFileMetaResponse with uploaded file metadata on success,
		NoDataResponse with error details on failure
	"""
	msg,rid,code,rescode = "OK",300,RES_CODE.FILE,status.HTTP_200_OK
	db_file_meta = None
	log_api(f"Calling routes::file::upload_file", level="INFO")
	try:
		# Create FileMetaCreate object from form fields
		_data = FileMetaCreate(
			file_type=file_type,
			name=name,
			store_type=store_type
		)
		
		# Get file object and size
		file_obj = file.file
		size = None
		try:
			# get size
			file_obj.seek(0, os.SEEK_END)
			size = file_obj.tell()
			file_obj.seek(0)
		except Exception:
			# fallback: read into memory (only if tiny) - better in prod to stream to temp file
			content = await file.read()
			size = len(content)
			from io import BytesIO
			file_obj = BytesIO(content)
			file_obj.seek(0)
		
		content_type = file.content_type or "application/octet-stream"
		filename = _data.name or file.filename or "unnamed_file"
		filename = filename.replace("/", "_")
		file_type_value = _data.file_type or content_type.split("/")[0] or "unknown"
		s3_key = f"{current_user.id}/{file_type_value}/{filename}"

		uploaded = False
		if _data.store_type == FileStore.RUSTFS:
			uploaded = upload_file_to_rustfs(file_obj, settings.RUSTFS_BUCKET, s3_key, content_type, size, filename)
			# print("UPLOADED", uploaded)
		if not uploaded:
			rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
			code = code+rid+1
			msg = "Failed to upload file to file storage"
			log_api(f"Failed to upload file to file storage [{code}]: {msg}", level="ERROR")
		else:
			_data2 = FileMetaCreateDB(
				size=size,
				content_type=content_type,
				rustfs_key=None,
				minio_key=None,
				file_type=file_type_value,
				name=filename,
				store_type=_data.store_type
			)
			if _data2.store_type == FileStore.RUSTFS:
				_data2.rustfs_key = s3_key
			elif _data2.store_type == FileStore.MINIO:
				_data2.minio_key = s3_key
			db_file_meta = file_meta_service.create_file_meta(db_write, db_read, _data2, current_user.id)
			if not db_file_meta:
				rescode = status.HTTP_400_BAD_REQUEST
				code = code+rid+2	
				msg = "Failed to create file metadata"
				log_api(f"Failed to create file metadata [{code}]: {msg}", level="ERROR")

				if _data.store_type == FileStore.RUSTFS:
					log_api(f"Removing file from rustfs [{code}]: {s3_key}", level="INFO")
					remove_file_from_rustfs(s3_key, settings.RUSTFS_BUCKET)
			else:
				code = code+RES_CODE.OK_CODE+rid
				rescode = status.HTTP_201_CREATED
				log_api(f"File uploaded [{code}]: {db_file_meta.name}", level="INFO")
	except Exception as e:
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		code = code+rid
		msg = str(e)
		log_api(f"Failed to upload file [{code}]: {e}", level="ERROR")
	
	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JsonFileMetaResponse(
			stat=True,
			msg=msg,
			code=code,
			dt=db_file_meta
		)