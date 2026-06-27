from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.auth.models import RefreshToken


def create(db: Session, refresh_token: RefreshToken) -> RefreshToken:
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_by_token(db: Session, token: str) -> RefreshToken | None:
    query = select(RefreshToken).where(RefreshToken.token == token, RefreshToken.revoked == False)
    return db.execute(query).scalar_one_or_none()


def revoke(db: Session, refresh_token: RefreshToken) -> None:
    refresh_token.revoked = True
    db.commit()


def revoke_all_for_user(db: Session, user_id: int) -> None:
    query = select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
    tokens = db.execute(query).scalars().all()
    for token in tokens:
        token.revoked = True
    db.commit()


def delete_expired(db: Session) -> int:
    query = select(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC))
    tokens = db.execute(query).scalars().all()
    count = len(tokens)
    for token in tokens:
        db.delete(token)
    db.commit()
    return count
