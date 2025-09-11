"""
Authentication service using fastapi-login LoginManager.

This module provides authentication functionality using the fastapi-login library
with JWT token management and Redis-based session handling.

Features:
	- User authentication with LoginManager
	- JWT token generation and validation
	- Redis-based token whitelisting and blacklisting
	- Session management and cleanup
"""

from datetime import timedelta
import time
import uuid
import jwt
from typing import Optional
from fastapi_login import LoginManager

from app.core.config import settings
from app.core.redis_client import redis_client, REDIS_KEY_PREFIX
from app.models.user import User
from app.utils.logger import log_api
from app.middlewares.context import get_tx_id, get_route

# Token expiration configuration
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_EXPIRE_MINUTES 
REFRESH_TOKEN_EXPIRE_MINUTES = settings.JWT_REFRESH_EXPIRE_MINUTES
BLACKLIST_EXPIRE_SECONDS = settings.JWT_BLACKLIST_EXPIRE_SECONDS


class LoginManagerAuthService:
	"""
	Authentication service using fastapi-login LoginManager.
	
	This service provides JWT-based authentication with Redis session management,
	integrating with the fastapi-login library for user management.
	"""
	
	def __init__(self, manager: LoginManager):
		"""
		Initialize the authentication service.
		
		Args:
			manager (LoginManager): The LoginManager instance to use for authentication.
		"""
		self.manager = manager
	
	def add_token_whitelist(self, user_id: int, jti: str) -> None:
		"""
		Add token JTI to Redis whitelist for a specific user.
		
		Args:
			user_id (int): The user ID.
			jti (str): The JWT ID to add to whitelist.
		"""
		tx_id = get_tx_id()
		route = get_route()
		try:
			redis_client.sadd(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", jti)
			redis_client.expire(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", ACCESS_TOKEN_EXPIRE_MINUTES * 60)
			log_api(
				f"Token added to whitelist: {jti}", 
				user=str(user_id), 
				route=route, 
				act="auth", 
				tx_id=tx_id, 
				level="INFO"
			)
		except Exception as e:
			log_api(
				f"Failed to add token to whitelist: {e}", 
				user=str(user_id), 
				route=route, 
				act="auth", 
				tx_id=tx_id, 
				level="ERROR"
			)
	
	def remove_token_whitelist(self, user_id: int, jti: str) -> None:
		"""
		Remove token JTI from Redis whitelist for a specific user.
		
		Args:
			user_id (int): The user ID.
			jti (str): The JWT ID to remove from whitelist.
		"""
		try:
			redis_client.srem(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", jti)
			log_api(
				f"Token removed from whitelist: {jti}", 
				user=str(user_id), 
				act="auth", 
				level="INFO"
			)
		except Exception as e:
			log_api(
				f"Failed to remove token from whitelist: {e}", 
				user=str(user_id), 
				act="auth", 
				level="ERROR"
			)
	
	def blacklist_token(self, token: str, user_id: int) -> None:
		"""
		Add token JTI to Redis blacklist and remove from whitelist.
		
		Args:
			token (str): The JWT token to blacklist.
			user_id (int): The user ID.
		"""
		try:
			payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			jti = payload.get("jti")
			uniq_key = payload.get("_key")
			
			# Add to blacklist
			redis_client.sadd(f"{REDIS_KEY_PREFIX}:blacklist:{user_id}", jti)
			redis_client.expire(f"{REDIS_KEY_PREFIX}:blacklist:{user_id}", BLACKLIST_EXPIRE_SECONDS)
			
			# Remove from whitelist
			self.remove_token_whitelist(user_id, jti)
			
			log_api(
				f"Token blacklisted: user_id={user_id} uniq_key={uniq_key} jti={jti}",
				user=str(user_id),
				act="auth_log",
				tx_id=uniq_key,
				level="INFO"
			)
		except Exception as e:
			log_api(
				f"Failed to blacklist token: {e}", 
				user=str(user_id), 
				act="auth", 
				level="ERROR"
			)
	
	def is_token_blacklisted(self, token: str, user_id: int) -> bool:
		"""
		Check if token JTI is in Redis blacklist.
		
		Args:
			token (str): The JWT token to check.
			user_id (int): The user ID.
			
		Returns:
			bool: True if token is blacklisted, False otherwise.
		"""
		try:
			payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			jti = payload.get("jti")
			return redis_client.sismember(f"{REDIS_KEY_PREFIX}:blacklist:{user_id}", jti)
		except Exception:
			return True
	
	def verify_token(self, token: str, user_id: int) -> Optional[dict]:
		"""
		Verify token: must be in whitelist and not in blacklist.
		
		Args:
			token (str): The JWT token to verify.
			user_id (int): The user ID.
			
		Returns:
			Optional[dict]: JWT payload if valid, None otherwise.
		"""
		try:
			payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			jti = payload.get("jti")
			
			# Check if token is blacklisted
			if self.is_token_blacklisted(token, user_id):
				return None
			
			# Check if token is in whitelist
			if not redis_client.sismember(f"{REDIS_KEY_PREFIX}:whitelist:{user_id}", jti):
				return None
			
			return payload
		except Exception:
			return None
	
	def create_access_token(self, user: User) -> str:
		"""
		Create access token using LoginManager and add to whitelist.
		
		Args:
			user (User): The user object.
			
		Returns:
			str: The generated access token.
		"""
		tx_id = get_tx_id()
		route = get_route()
		
		log_api(
			f"Creating access token for user: {user.username}", 
			user=str(user.id), 
			route=route, 
			act="auth", 
			tx_id=tx_id, 
			level="INFO"
		)
		
		try:
			# Create token using LoginManager
			data = {
				"sub": str(user.id),
				"jti": str(uuid.uuid4()),
				"_key": str(uuid.uuid4()),
				"exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
			}
			token = self.manager.create_access_token(data=data,expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
			
			# Decode token to get JTI for whitelist management
			payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			jti = payload.get("jti", str(uuid.uuid4()))
			
			# Add to whitelist
			self.add_token_whitelist(user.id, jti)
			
			log_api(
				f"Access token created successfully", 
				user=str(user.id), 
				route=route, 
				act="auth", 
				tx_id=tx_id, 
				level="INFO"
			)
			
			return token
		except Exception as e:
			log_api(
				f"Failed to create access token: {e}", 
				user=str(user.id), 
				route=route, 
				act="auth", 
				tx_id=tx_id, 
				level="ERROR"
			)
			return None
	
	def create_refresh_token(self, user_id: int, uniq_key: str) -> str:
		"""
		Create refresh token JWT with uniq_key.
		
		Args:
			user_id (int): The user ID.
			uniq_key (str): Unique key from access token.
			
		Returns:
			str: The generated refresh token.
		"""
		tx_id = get_tx_id()
		route = get_route()
		
		log_api(
			f"Creating refresh token for user: {user_id}", 
			user=str(user_id), 
			route=route, 
			act="auth", 
			tx_id=tx_id, 
			level="INFO"
		)
		
		try:
			payload = {
				"sub": str(user_id),
				"jti": str(uuid.uuid4()),
				"_key": uniq_key,
				"exp": int(time.time()) + REFRESH_TOKEN_EXPIRE_MINUTES * 60,
			}
			token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
			
			# Add to whitelist
			self.add_token_whitelist(user_id, payload["jti"])
			
			log_api(
				f"Refresh token created successfully", 
				user=str(user_id), 
				route=route, 
				act="auth", 
				tx_id=tx_id, 
				level="INFO"
			)
			
			return token
		except Exception as e:
			log_api(
				f"Failed to create refresh token: {e}", 
				user=str(user_id), 
				route=route, 
				act="auth", 
				tx_id=tx_id, 
				level="ERROR"
			)
			return None
	
	def refresh_access_token(self, refresh_token: str, user_id: int) -> Optional[str]:
		"""
		Refresh access token, clear whitelist, and create new access token.
		
		Args:
			refresh_token (str): The refresh token.
			user_id (int): The user ID.
			
		Returns:
			Optional[str]: New access token if successful, None otherwise.
		"""
		try:
			payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
			if int(payload["exp"]) < int(time.time()):
				return None
			
			uniq_key = payload.get("_key")
			
			# Clear whitelist for user
			whitelist_key = f"{REDIS_KEY_PREFIX}:whitelist:{user_id}"
			redis_client.delete(whitelist_key)
			
			log_api(
				f"Token refresh: user_id={user_id} uniq_key={uniq_key}",
				user=str(user_id),
				act="auth_log",
				tx_id=uniq_key,
				level="INFO"
			)
			
			# Create new access token with same uniq_key
			return self.create_access_token_with_uniq(user_id, uniq_key)
		except Exception as e:
			log_api(
				f"Failed to refresh access token: {e}", 
				user=str(user_id), 
				act="auth", 
				level="ERROR"
			)
			return None
	
	def create_access_token_with_uniq(self, user_id: int, uniq_key: str) -> str:
		"""
		Create access token JWT with specific uniq_key (for refresh).
		
		Args:
			user_id (int): The user ID.
			uniq_key (str): Unique key to include in token.
			
		Returns:
			str: The generated access token.
		"""
		try:
			payload = {
				"sub": str(user_id),
				"jti": str(uuid.uuid4()),
				"_key": uniq_key,
				"exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
			}
			token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
			self.add_token_whitelist(user_id, payload["jti"])
			return token
		except Exception as e:
			log_api(
				f"Failed to create access token with uniq_key: {e}", 
				user=str(user_id), 
				act="auth", 
				level="ERROR"
			)
			return None
