# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    require_permissions,
    serialize_user,
)

router = APIRouter(prefix='/auth', tags=['auth'])


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreateRequest(BaseModel):
    username: str
    full_name: str
    password: str
    role: str


@router.post('/login')
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username.strip(), payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    return {
        'access_token': create_access_token(user),
        'token_type': 'bearer',
        'user': serialize_user(user),
    }


@router.get('/me')
def me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@router.get('/users')
def list_users(
    _: User = Depends(require_permissions('user_admin')),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.role.asc(), User.full_name.asc()).all()
    return [serialize_user(user) for user in users]


@router.post('/users')
def create_user(
    payload: UserCreateRequest,
    _: User = Depends(require_permissions('user_admin')),
    db: Session = Depends(get_db),
):
    if payload.role not in {'desk_officer', 'legal_translator', 'it_admin'}:
        raise HTTPException(status_code=400, detail='Unsupported role')
    existing = db.query(User).filter(User.username == payload.username.strip()).first()
    if existing:
        raise HTTPException(status_code=409, detail='Username already exists')
    user = User(
        username=payload.username.strip(),
        full_name=payload.full_name.strip() or payload.username.strip(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return serialize_user(user)
