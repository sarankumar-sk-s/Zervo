from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_active_user
from app.models.food import FoodListing, FoodRequest
from app.models.user import User
from app.schemas.food import FoodListingResponse

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    listings = db.query(FoodListing).all()
    available = [
        FoodListingResponse(
            id=item.id,
            donorId=item.donor_id,
            donorName=item.donor_name,
            organisation=item.organisation,
            foodType=item.food_type,
            quantity=item.quantity,
            location=item.location,
            cookedTime=item.cooked_time,
            pickupTime=item.pickup_time,
            contact=item.contact,
            status=item.status,
            photo=item.photo
        )
        for item in listings if item.status == "available"
    ]
    completed_count = sum(1 for item in listings if item.status == "completed")
    
    # Leaderboard from users
    top_users = db.query(User).filter(User.role == "volunteer").order_by(User.points.desc()).limit(10).all()
    leaderboard = [
        {"name": u.name, "points": u.points, "deliveries": u.deliveries}
        for u in top_users
    ]
    
    return {
        "available_pickups": available,
        "total_listings": len(listings),
        "completed_pickups": completed_count,
        "meals_served": completed_count * 10 if completed_count > 0 else len(listings) * 5,
        "leaderboard": leaderboard
    }


@router.post("/claim/{food_id}")
def claim_pickup(
    food_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    listing = db.query(FoodListing).filter(FoodListing.id == food_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food listing not found")

    if listing.status != "available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Listing already claimed or completed")

    listing.status = "claimed"
    listing.claimed_by_id = current_user.id
    db.add(listing)
    db.commit()

    return {"message": "Pickup claimed successfully", "food_id": food_id}


@router.post("/deliver/{food_id}")
def deliver_pickup(
    food_id: str,
    payload: Dict[str, Any] = {},
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    listing = db.query(FoodListing).filter(FoodListing.id == food_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food listing not found")

    listing.status = "completed"
    if payload.get("photo"):
        listing.photo = payload.get("photo")

    current_user.points += 50
    current_user.deliveries += 1

    db.add(listing)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Delivery marked as complete!",
        "points": current_user.points,
        "deliveries": current_user.deliveries
    }
