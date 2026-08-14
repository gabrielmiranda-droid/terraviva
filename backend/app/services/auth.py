from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User
from app.schemas.token import Token


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def build_token_pair(user: User) -> Token:
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
