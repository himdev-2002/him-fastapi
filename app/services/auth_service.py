import time
import uuid
import jwt
from typing import Optional

from app.core.config import settings
from app.core.redis_client import redis_client, REDIS_KEY_PREFIX
from app.models.user import User
from app.utils.logger import log_api
from app.middlewares.context import get_tx_id, get_route
# Konfigurasi waktu kadaluarsa token diambil dari .env/config
# Menentukan masa berlaku access token (menit)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_EXPIRE_MINUTES 
# Masa berlaku refresh token (menit)
REFRESH_TOKEN_EXPIRE_MINUTES = settings.JWT_REFRESH_EXPIRE_MINUTES
# Masa berlaku blacklist token (detik)
BLACKLIST_EXPIRE_SECONDS = settings.JWT_BLACKLIST_EXPIRE_SECONDS

class JWTSession:
	@staticmethod
	def add_token_whitelist(user_id: int, jti: str):
		"""
		Menambahkan jti token ke whitelist Redis untuk user tertentu.
		Digunakan untuk menandai token yang aktif.
		"""
		tx_id = get_tx_id()
		route = get_route()
		try:
			redis_client.sadd(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", jti)
			redis_client.expire(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", ACCESS_TOKEN_EXPIRE_MINUTES * 60)
		except Exception as e:
			log_api(f"Failed Add Token Whitelist: {e}", user=str(user_id), route=route, act="auth", tx_id=tx_id, level="ERROR")
			return None

	@staticmethod
	def remove_token_whitelist(user_id: int, jti: str):
		"""
		Menghapus jti token dari whitelist Redis user tertentu.
		Digunakan saat logout atau refresh agar token tidak lagi aktif.
		"""
		redis_client.srem(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", jti)

	@staticmethod
	def get_active_users():
		"""
		Mengambil daftar user_id yang memiliki token aktif (whitelist tidak kosong).
		"""
		keys = redis_client.keys(f"{REDIS_KEY_PREFIX}:whitelist:*")
		return [k.split(":")[-1] for k in keys if redis_client.scard(k) > 0]

	@staticmethod
	def create_access_token(user: User) -> str:
		"""
		Membuat access token JWT baru dan menambahkannya ke whitelist.
		"""
		tx_id = get_tx_id()
		route = get_route()
		log_api(f"Creating access token for user: {user}", user=str(user.id), route=route, act="auth", tx_id=tx_id, level="INFO")
		try:
			payload = {
				"sub": str(user.id),
				"jti": str(uuid.uuid4()),
				"_key": str(uuid.uuid4()),
				"exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
			}
			token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
			log_api(f"Access token created: {token}", user=str(user.id), route=route, act="auth", tx_id=tx_id, level="INFO")
			log_api(f"Adding token to whitelist: {payload['jti']}", user=str(user.id), route=route, act="auth", tx_id=tx_id, level="INFO")
			JWTSession.add_token_whitelist(user.id, payload["jti"])
			log_api(f"Token added to whitelist: {payload['jti']}", user=str(user.id), route=route, act="auth", tx_id=tx_id, level="INFO")
			return token
		except Exception as e:
			log_api(f"Failed Generate Access Token: {e}", user=str(user.id), route=route, act="auth", tx_id=tx_id, level="ERROR")
			return None

	@staticmethod
	def create_refresh_token(user_id: int, uniq_key: str) -> str:
		"""
		Membuat refresh token JWT baru untuk user tertentu, membawa uniq_key dari access token.
		"""
		tx_id = get_tx_id()
		route = get_route()
		log_api(f"Creating refresh token for user: {user_id}", user=str(user_id), route=route, act="auth", tx_id=tx_id, level="INFO")
		payload = {
			"sub": str(user_id),
			"jti": str(uuid.uuid4()),
			"_key": uniq_key,
			"exp": int(time.time()) + REFRESH_TOKEN_EXPIRE_MINUTES * 60,
		}
		token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
		log_api(f"Refresh token created: {token}", user=str(user_id), route=route, act="auth", tx_id=tx_id, level="INFO")
		# log_api(f"Adding token to whitelist: {payload['jti']}", user=str(user_id), route=route, act="auth", tx_id=tx_id, level="INFO")
		# JWTSession.add_token_whitelist(user_id, payload["jti"])
		# log_api(f"Token added to whitelist: {payload['jti']}", user=str(user_id), route=route, act="auth", tx_id=tx_id, level="INFO")
		return token

	@staticmethod
	def blacklist_token(token: str, user_id: int):
		"""
		Memasukkan jti token ke blacklist Redis dan menghapus dari whitelist.
		Digunakan saat logout agar token tidak bisa digunakan lagi.
		"""
		try:
			payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			jti = payload.get("jti")
			uniq_key = payload.get("_key")
			redis_client.sadd(f"{REDIS_KEY_PREFIX}:blacklist:{user_id}", jti)
			redis_client.expire(f"{REDIS_KEY_PREFIX}:blacklist:{user_id}", BLACKLIST_EXPIRE_SECONDS)
			JWTSession.remove_token_whitelist(user_id, jti)
			log_api(
				msg=f"LOGOUT: user_id={user_id} uniq_key={uniq_key} jti={jti}",
				user=str(user_id),
				act="auth",
				tx_id=uniq_key,
				level="INFO"
			)
		except Exception:
			pass

	@staticmethod
	def is_token_blacklisted(token: str, user_id: int) -> bool:
		"""
		Mengecek apakah token (jti) sudah masuk blacklist Redis.
		"""
		try:
			payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			jti = payload.get("jti")
			return redis_client.sismember(f"{REDIS_KEY_PREFIX}:blacklist:{user_id}", jti)
		except Exception:
			return True

	@staticmethod
	def verify_access_token(token: str, is_refresh: bool = False) -> Optional[dict]:
		"""
		Validasi token: harus ada di whitelist dan tidak ada di blacklist.
		Jika valid, return payload JWT, jika tidak return None.
		"""
		log_api(f"Verifying access token: {token} is_refresh: {is_refresh}", act="auth", level="DEBUG")
		try:
			options={}
			if is_refresh:
				options={"verify_exp": False}
			payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options=options)
			# if not is_refresh and int(payload["exp"]) < int(time.time()):
			# 	return None
			if not is_refresh:
				jti = payload.get("jti")
				user_id = payload.get("sub")
				is_blacklist = redis_client.sismember(f"{REDIS_KEY_PREFIX}:blacklist:{user_id}", jti)
				is_whitelist = redis_client.sismember(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", jti)
				log_api(f"is blacklist: {is_blacklist}", act="auth", level="DEBUG")
				log_api(f"is whitelist: {is_whitelist}", act="auth", level="DEBUG") 
				if is_blacklist:
					return None
				if not is_whitelist:
					return None
			return payload
		except Exception as e:
			log_api(f"Failed to verify access token: {e}", act="auth", level="ERROR")
			return None

	@staticmethod
	def refresh_access_token(access_token: str, refresh_token: str, user_id: int) -> Optional[str]:
		"""
		Melakukan refresh access token, menghapus semua token whitelist user,
		lalu membuat access token baru.
		"""
		try:
			payload1 = jwt.decode(access_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			uniq_key1 = payload.get("_key")
			payload2 = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			uniq_key2 = payload.get("_key")
			jti = payload.get("jti")
			JWTSession.remove_token_whitelist(user_id, jti)
			log_api(
				msg=f"REFRESH: user_id={user_id} uniq_key={uniq_key}",
				user=str(user_id),
				act="auth",
				tx_id=uniq_key,
				level="INFO"
			)
			# Buat access token baru dengan uniq_key yang sama
			return JWTSession.create_access_token_with_uniq(user_id, uniq_key)
		except Exception:
			return None

	@staticmethod
	def create_access_token_with_uniq(user_id: int, uniq_key: str) -> str:
		"""
		Membuat access token JWT baru dengan uniq_key tertentu (untuk refresh).
		"""
		payload = {
			"sub": str(user_id),
			"jti": str(uuid.uuid4()),
			"_key": uniq_key,
			"exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
		}
		token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
		JWTSession.add_token_whitelist(user_id, payload["jti"])
		return token
