from fastapi import APIRouter, HTTPException, status
from src.admin import service
from src.users.schemas import UserResponse
from src.core.exceptions import UserNotFoundError
from src.dependencies.auth import CurrentOwner
from src.dependencies.db import DbSession

router = APIRouter(prefix="/owner", tags=["Owner"])


@router.post("/promote/{user_id}", response_model=UserResponse)
def promote_to_admin(user_id: int, db: DbSession, current_owner: CurrentOwner):
    try:
        return service.promote_to_admin(db, user_id, current_owner)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
