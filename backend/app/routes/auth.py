from fastapi import APIRouter, Depends, HTTPException, status

from app.database import db
from app.dependencies import get_current_user_out
from app.models import Role, TokenOut, UserCreate, UserLogin, UserOut
from app.security import create_access_token, hash_password, verify_password
from app.utils import now_utc, serialize_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate) -> dict:
    email = payload.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user_count = await db.users.count_documents({})
    role = Role.admin.value if user_count == 0 else Role.member.value
    user_doc = {
        "name": payload.name.strip(),
        "email": email,
        "password_hash": hash_password(payload.password),
        "role": role,
        "created_at": now_utc(),
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    token = create_access_token(str(result.inserted_id), {"role": role})
    return {"access_token": token, "user": serialize_user(user_doc)}


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin) -> dict:
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(str(user["_id"]), {"role": user["role"]})
    return {"access_token": token, "user": serialize_user(user)}


@router.get("/me", response_model=UserOut)
async def me(user: dict = Depends(get_current_user_out)) -> dict:
    return user
