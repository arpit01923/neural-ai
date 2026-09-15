from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.params import Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dependencies import get_db
from models import User
from jose import JWTError, jwt
from pwdlib import PasswordHash
from config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)


def create_access_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
# Check user exist or not 
async def get_current_user(access_token: str | None = Cookie(default=None), db: AsyncSession = Depends(get_db)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user