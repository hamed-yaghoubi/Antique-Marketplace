from sqlalchemy.orm import Session
from src.core.exceptions import UserNotFoundError
from src.users.models import User
from src.users import repository
from src.users.schemas import UserUpdate



def get_user(db: Session, user_id: int) -> User:
    user = repository.get_by_id(db, user_id)

    if user is None:
        raise UserNotFoundError()

    return user

def get_user_by_username(db: Session, username: str) -> User:
    user = repository.get_by_username(db, username)

    if user is None:
        raise UserNotFoundError()

    return user

def update_user(db: Session, user: User, data: UserUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    return repository.update(db, user)

def delete_user(db: Session, user: User) -> None:
    repository.delete(db, user)
