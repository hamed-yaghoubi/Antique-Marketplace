from fastapi import APIRouter
from src.users import service
from src.users.schemas import UserResponse
from src.dependencies.auth import CurrentOwner
from src.dependencies.db import DbSession

router = APIRouter(prefix="/owner", tags=["Owner"])


@router.post("/promote/{user_id}", response_model=UserResponse)
def promote_to_admin(user_id: int, db: DbSession, current_owner: CurrentOwner):
    return service.promote_to_admin(db, user_id, current_owner)


@router.post("/demote/{user_id}", response_model=UserResponse)
def demote_to_user(user_id: int, db: DbSession, current_owner: CurrentOwner):
    return service.demote_to_user(db, user_id, current_owner)
