from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import RoleName
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User


def seed_initial_data() -> None:
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_admin(db)
        db.commit()
    finally:
        db.close()


def seed_roles(db: Session) -> None:
    existing = {role.name for role in db.query(Role).all()}
    for role_name in RoleName:
        if role_name.value not in existing:
            db.add(Role(name=role_name.value, description=f"Perfil {role_name.value}"))
    db.flush()


def seed_admin(db: Session) -> None:
    admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
    if admin:
        return
    admin_role = db.query(Role).filter(Role.name == RoleName.ADMIN.value).one()
    db.add(
        User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            full_name=settings.FIRST_SUPERUSER_NAME,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            role=admin_role,
            is_active=True,
        )
    )


if __name__ == "__main__":
    seed_initial_data()
