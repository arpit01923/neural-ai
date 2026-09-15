from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import settings
from dependencies import get_db
from models import User
from jose import JWTError, jwt
from schemas.user import UserCreate, UserLogin, Token
from utils.auth import  hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Register
@router.post("/register")
async def register(user: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(firstname=user.firstname,lastname=user.lastname,email=user.email,hashed_password=hash_password(user.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    token = create_access_token(user.email)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,      # True after HTTPS deployment
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )
    return { 
        "message": "User registered successfully",
        "user": {
            "id": str(new_user.id),
            "firstname": new_user.firstname,
            "lastname": new_user.lastname,
            "email": new_user.email,
            "created_at": new_user.created_at,
        }
    }


# Login
@router.post("/login")
async def login(user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user.password, db_user.hashed_password,):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(db_user.email)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,      # True in production
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return {
        "message": "Login successful",
        "user": {
            "id": str(db_user.id),
            "firstname": db_user.firstname,
            "lastname": db_user.lastname,
            "email": db_user.email,
            "created_at": db_user.created_at,
        }
    }
    
# Logout
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")

    return {
        "message": "Logged out successfully"
    }

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "firstname": current_user.firstname,
        "lastname": current_user.lastname,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }