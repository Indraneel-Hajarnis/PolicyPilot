import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Callable

# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal, get_db
from app.db.models import User

security = HTTPBearer(auto_error=False)
PBKDF2_ITERATIONS = 160_000

ROLE_PERMISSIONS = {
    'desk_officer': ['upload', 'chat', 'summary', 'documents', 'compare', 'repository_browse'],
    'legal_translator': ['chat', 'summary', 'documents', 'compare', 'repository_browse'],
    'it_admin': [
        'upload',
        'chat',
        'summary',
        'documents',
        'analytics',
        'compare',
        'repository_browse',
        'repository_manage',
        'user_admin',
    ],
}


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode('utf-8').rstrip('=')


def _b64decode(raw: str) -> bytes:
    padding = '=' * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return f'{PBKDF2_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}'


def verify_password(password: str, password_hash: str) -> bool:
    try:
        iterations_raw, salt_raw, digest_raw = password_hash.split('$', 2)
        iterations = int(iterations_raw)
        salt = _b64decode(salt_raw)
        expected = _b64decode(digest_raw)
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return hmac.compare_digest(actual, expected)


def serialize_user(user: User) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role,
        'permissions': ROLE_PERMISSIONS.get(user.role, []),
        'is_active': user.is_active,
    }


def create_access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_token_ttl_minutes)
    payload = {
        'sub': user.id,
        'role': user.role,
        'username': user.username,
        'exp': int(expires_at.timestamp()),
    }
    payload_raw = _b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signature = hmac.new(settings.auth_secret.encode('utf-8'), payload_raw.encode('utf-8'), hashlib.sha256).digest()
    return f'{payload_raw}.{_b64encode(signature)}'


def decode_access_token(token: str) -> dict:
    try:
        payload_raw, signature_raw = token.split('.', 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token') from exc

    expected = hmac.new(settings.auth_secret.encode('utf-8'), payload_raw.encode('utf-8'), hashlib.sha256).digest()
    actual = _b64decode(signature_raw)
    if not hmac.compare_digest(expected, actual):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token')

    payload = json.loads(_b64decode(payload_raw).decode('utf-8'))
    if payload.get('exp', 0) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication token expired')
    return payload


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')
    payload = decode_access_token(credentials.credentials)
    user = db.query(User).filter(User.id == payload.get('sub')).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User account is unavailable')
    return user


def require_permissions(*permissions: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        granted = set(ROLE_PERMISSIONS.get(current_user.role, []))
        missing = [permission for permission in permissions if permission not in granted]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Missing required permission(s): {", ".join(missing)}',
            )
        return current_user

    return dependency


def ensure_default_users() -> None:
    seed_users = [
        ('desk_officer', settings.seed_desk_officer_username, 'Desk Officer', settings.seed_desk_officer_password),
        ('legal_translator', settings.seed_legal_translator_username, 'Legal Translator', settings.seed_legal_translator_password),
        ('it_admin', settings.seed_it_admin_username, 'IT Administrator', settings.seed_it_admin_password),
    ]
    db = SessionLocal()
    try:
        for role, username, full_name, password in seed_users:
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                if existing.role != role:
                    existing.role = role
                if not existing.password_hash:
                    existing.password_hash = hash_password(password)
                if not existing.full_name:
                    existing.full_name = full_name
                existing.is_active = True
                continue
            db.add(
                User(
                    username=username,
                    full_name=full_name,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True,
                )
            )
        db.commit()
    finally:
        db.close()
