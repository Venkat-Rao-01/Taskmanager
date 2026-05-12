from fastapi import APIRouter, Depends

from app.database import db
from app.dependencies import get_current_user, require_admin
from app.models import UserOut
from app.utils import serialize_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserOut])
async def list_users(_: dict = Depends(get_current_user)) -> list[dict]:
    users = await db.users.find({}, {"password_hash": 0}).sort("name", 1).to_list(200)
    return [serialize_user(user) for user in users]


@router.patch("/{user_id}/promote", response_model=UserOut)
async def promote_user(user_id: str, _: dict = Depends(require_admin)) -> dict:
    from app.utils import oid

    target_id = oid(user_id)
    await db.users.update_one({"_id": target_id}, {"$set": {"role": "Admin"}})
    user = await db.users.find_one({"_id": target_id})
    return serialize_user(user)
