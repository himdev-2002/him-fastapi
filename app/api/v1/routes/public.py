from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.logger import log_api
from app.schemas.public import HashResponse, HashRequest,VerifyResponse, VerifyRequest

try:
    # prefer passlib if installed
    from passlib.hash import bcrypt
    def make_bcrypt(pw: str) -> str:
        return bcrypt.hash(pw)
except Exception:
    import bcrypt as _bcrypt
    def make_bcrypt(pw: str) -> str:
        return _bcrypt.hashpw(pw.encode('utf-8'), _bcrypt.gensalt()).decode()


router = APIRouter(prefix="/public", tags=["public"])


@router.post("/bcrypt", response_model=HashResponse)
def gen_bcrypt(payload: HashRequest):
    if not payload.password:
        raise HTTPException(status_code=400, detail="password required")
    h = make_bcrypt(payload.password)
    log_api(msg="Generated password bcrypt hash", act="auth", level="INFO")
    return HashResponse(hash=h)

@router.post("/bcrypt/verify", response_model=VerifyResponse)
def verify_bcrypt(payload: VerifyRequest):
    from app.utils.helpers import verify_password
    valid = verify_password(payload.password, payload.hash)
    log_api(msg=f"Verify password result={valid}", act="auth", level="INFO")
    return VerifyResponse(valid=valid)
