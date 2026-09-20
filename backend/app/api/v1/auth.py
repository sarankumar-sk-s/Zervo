from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered."
        )

    user = User(
        email=user_in.email.lower(),
        name=user_in.name,
        phone=user_in.phone or "",
        hashed_password=get_password_hash(user_in.password),
        role=""
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=user.id)
    user_res = UserResponse(
        uid=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        points=user.points,
        deliveries=user.deliveries
    )
    return Token(access_token=access_token, user=user_res)


@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email.lower()).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(subject=user.id)
    user_res = UserResponse(
        uid=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        points=user.points,
        deliveries=user.deliveries
    )
    return Token(access_token=access_token, user=user_res)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        uid=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        points=current_user.points,
        deliveries=current_user.deliveries
    )
