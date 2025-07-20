from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.users import get_user_by_username, verify_password
from auth.jwt_handler import create_access_token
from database import get_db
from sqlalchemy.orm import Session


router = APIRouter()

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user_by_username(form_data.username,db)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    return {
        "access_token": create_access_token({"sub": user.username}),
        "token_type": "bearer"
    }
