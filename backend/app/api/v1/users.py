from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserRoleUpdate, PasswordChange

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        uid=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        points=current_user.points,
        deliveries=current_user.deliveries
    )


@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.phone is not None:
        current_user.phone = user_update.phone

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return UserResponse(
        uid=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        points=current_user.points,
        deliveries=current_user.deliveries
    )


@router.put("/role", response_model=UserResponse)
def update_role(
    role_update: UserRoleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    current_user.role = role_update.role
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return UserResponse(
        uid=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        points=current_user.points,
        deliveries=current_user.deliveries
    )


@router.post("/password")
def change_password(
    pwd_in: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not verify_password(pwd_in.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password."
        )

    current_user.hashed_password = get_password_hash(pwd_in.new_password)
    db.add(current_user)
    db.commit()

    return {"message": "Password updated successfully"}
