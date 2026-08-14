from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.token import LoginRequest, Token
from app.schemas.user import UserRead
from app.services.auth import authenticate_user, build_token_pair

router = APIRouter()


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha invalidos.",
        )
    return build_token_pair(user)


@router.get("/me", response_model=UserRead)
def read_me(current_user=Depends(get_current_user)):
    return current_user
