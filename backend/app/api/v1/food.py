from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_active_user
from app.models.food import FoodListing, FoodRequest
from app.models.user import User
from app.schemas.food import FoodListingCreate, FoodListingResponse, FoodRequestCreate, FoodRequestResponse

router = APIRouter()


@router.post("/listings", response_model=FoodListingResponse)
def create_listing(
    listing_in: FoodListingCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    donor_id = current_user.id if current_user else None
    donor_name = listing_in.donorName or (current_user.name if current_user else "Anonymous Donor")

    pickup_addr = listing_in.pickup_address or listing_in.location

    listing = FoodListing(
        donor_id=donor_id,
        donor_name=donor_name,
        organisation=listing_in.organisation or "",
        food_type=listing_in.foodType,
        quantity=listing_in.quantity,
        location=listing_in.location,
        pickup_address=pickup_addr,
        latitude=listing_in.latitude,
        longitude=listing_in.longitude,
        cooked_time=listing_in.cookedTime or "",
        pickup_time=listing_in.pickupTime or "",
        contact=listing_in.contact,
        photo=listing_in.photo,
        status="available"
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    return FoodListingResponse(
        id=listing.id,
        donorId=listing.donor_id,
        donorName=listing.donor_name,
        organisation=listing.organisation,
        foodType=listing.food_type,
        quantity=listing.quantity,
        location=listing.location,
        pickup_address=listing.pickup_address,
        pickupAddress=listing.pickup_address,
        latitude=listing.latitude,
        longitude=listing.longitude,
        cookedTime=listing.cooked_time,
        pickupTime=listing.pickup_time,
        contact=listing.contact,
        status=listing.status,
        photo=listing.photo
    )


@router.get("/listings", response_model=List[FoodListingResponse])
def get_listings(db: Session = Depends(get_db)):
    listings = db.query(FoodListing).order_by(FoodListing.created_at.desc()).all()
    return [
        FoodListingResponse(
            id=item.id,
            donorId=item.donor_id,
            donorName=item.donor_name,
            organisation=item.organisation,
            foodType=item.food_type,
            quantity=item.quantity,
            location=item.location,
            pickup_address=item.pickup_address,
            pickupAddress=item.pickup_address,
            latitude=item.latitude,
            longitude=item.longitude,
            cookedTime=item.cooked_time,
            pickupTime=item.pickup_time,
            contact=item.contact,
            status=item.status,
            photo=item.photo
        )
        for item in listings
    ]


@router.post("/requests", response_model=FoodRequestResponse)
def create_request(
    request_in: FoodRequestCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    receiver_id = current_user.id if current_user else None

    req = FoodRequest(
        receiver_id=receiver_id,
        organisation=request_in.organisation,
        address=request_in.address,
        contact=request_in.contact,
        status="pending"
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return FoodRequestResponse(
        id=req.id,
        receiverId=req.receiver_id,
        organisation=req.organisation,
        address=req.address,
        contact=req.contact,
        status=req.status
    )


@router.get("/requests", response_model=List[FoodRequestResponse])
def get_requests(db: Session = Depends(get_db)):
    requests = db.query(FoodRequest).order_by(FoodRequest.created_at.desc()).all()
    return [
        FoodRequestResponse(
            id=item.id,
            receiverId=item.receiver_id,
            organisation=item.organisation,
            address=item.address,
            contact=item.contact,
            status=item.status
        )
        for item in requests
    ]
