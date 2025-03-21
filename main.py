from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from pydantic import BaseModel

import crud
import models
import schemas
import googlemapsapi
from database import get_db, init_db
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from dummy_data import create_dummy_data
from export_dummy_data import export_database_to_sql

# Initialize FastAPI app
app = FastAPI(
    title="TollEasy API",
    description="API for TollEasy toll management system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Load dummy data if the database is empty
    create_dummy_data()

# Authentication endpoints
@app.post("/api/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# User endpoints
@app.post("/api/users", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@app.put("/api/users/me", response_model=schemas.User)
def update_user_endpoint(
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.update_user(db=db, user_id=current_user.id, user=user)

# Vehicle endpoints
@app.get("/api/vehicles", response_model=List[schemas.Vehicle])
def read_vehicles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    vehicles = crud.get_vehicles_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return vehicles

@app.post("/api/vehicles", response_model=schemas.Vehicle)
def create_vehicle_endpoint(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Check if user has reached max vehicles limit based on subscription plan
    user_plan = crud.get_plan(db, current_user.subscription_plan_id) if current_user.subscription_plan_id else None
    if user_plan:
        user_vehicles_count = len(crud.get_vehicles_by_user(db, user_id=current_user.id))
        if user_vehicles_count >= user_plan.max_vehicles:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum number of vehicles ({user_plan.max_vehicles}) reached for your plan"
            )
    
    return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)

@app.get("/api/vehicles/{vehicle_id}", response_model=schemas.Vehicle)
def read_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    vehicle = crud.get_vehicle(db, vehicle_id=vehicle_id)
    if vehicle is None or vehicle.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@app.put("/api/vehicles/{vehicle_id}", response_model=schemas.Vehicle)
def update_vehicle_endpoint(
    vehicle_id: int,
    vehicle: schemas.VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_vehicle = crud.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None or db_vehicle.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return crud.update_vehicle(db=db, vehicle_id=vehicle_id, vehicle=vehicle)

@app.delete("/api/vehicles/{vehicle_id}", response_model=schemas.Vehicle)
def delete_vehicle_endpoint(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_vehicle = crud.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None or db_vehicle.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return crud.delete_vehicle(db=db, vehicle_id=vehicle_id)

# TollPlaza endpoints
@app.get("/api/toll-plazas", response_model=List[schemas.TollPlaza])
def read_toll_plazas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_toll_plazas(db, skip=skip, limit=limit)

@app.get("/api/toll-plazas/{toll_plaza_id}", response_model=schemas.TollPlaza)
def read_toll_plaza(
    toll_plaza_id: int,
    db: Session = Depends(get_db)
):
    toll_plaza = crud.get_toll_plaza(db, toll_plaza_id=toll_plaza_id)
    if toll_plaza is None:
        raise HTTPException(status_code=404, detail="Toll Plaza not found")
    return toll_plaza

# Admin-only endpoints for creating/updating toll plazas
@app.post("/api/admin/toll-plazas", response_model=schemas.TollPlaza)
def create_toll_plaza_endpoint(
    toll_plaza: schemas.TollPlazaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # In a real app, you'd check if the user is an admin here
    # For now, we'll just create the toll plaza
    return crud.create_toll_plaza(db=db, toll_plaza=toll_plaza)

@app.put("/api/admin/toll-plazas/{toll_plaza_id}", response_model=schemas.TollPlaza)
def update_toll_plaza_endpoint(
    toll_plaza_id: int,
    toll_plaza: schemas.TollPlazaUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # In a real app, you'd check if the user is an admin here
    db_toll_plaza = crud.get_toll_plaza(db, toll_plaza_id=toll_plaza_id)
    if db_toll_plaza is None:
        raise HTTPException(status_code=404, detail="Toll Plaza not found")
    
    return crud.update_toll_plaza(db=db, toll_plaza_id=toll_plaza_id, toll_plaza=toll_plaza)

# Plan endpoints
@app.get("/api/plans", response_model=List[schemas.Plan])
def read_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_plans(db, skip=skip, limit=limit)

@app.get("/api/plans/{plan_id}", response_model=schemas.Plan)
def read_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    plan = crud.get_plan(db, plan_id=plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

# Admin-only endpoints for creating/updating plans
@app.post("/api/admin/plans", response_model=schemas.Plan)
def create_plan_endpoint(
    plan: schemas.PlanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # In a real app, you'd check if the user is an admin here
    return crud.create_plan(db=db, plan=plan)

@app.put("/api/admin/plans/{plan_id}", response_model=schemas.Plan)
def update_plan_endpoint(
    plan_id: int,
    plan: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # In a real app, you'd check if the user is an admin here
    db_plan = crud.get_plan(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return crud.update_plan(db=db, plan_id=plan_id, plan=plan)

# Transaction endpoints
@app.get("/api/transactions", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.get_transactions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@app.post("/api/transactions", response_model=schemas.Transaction)
def create_transaction_endpoint(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Validate that the vehicle belongs to the user
    vehicle = crud.get_vehicle(db, vehicle_id=transaction.vehicle_id)
    if vehicle is None or vehicle.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Validate the toll plaza exists
    toll_plaza = crud.get_toll_plaza(db, toll_plaza_id=transaction.toll_plaza_id)
    if toll_plaza is None:
        raise HTTPException(status_code=404, detail="Toll Plaza not found")
    
    # Check if the user has enough balance for a toll payment
    if transaction.transaction_type == schemas.TransactionType.TOLL_PAYMENT and current_user.current_balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create the transaction
    db_transaction = crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)
    
    # Create notification
    if transaction.transaction_type == schemas.TransactionType.TOLL_PAYMENT:
        notification = schemas.NotificationCreate(
            message=f"Toll payment of ${transaction.amount:.2f} completed successfully at {toll_plaza.name}",
            type=schemas.NotificationType.TRANSACTION_COMPLETE
        )
        crud.create_notification(db=db, notification=notification, user_id=current_user.id)
    
    return db_transaction

@app.get("/api/transactions/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if transaction is None or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# Payment Method endpoints
@app.get("/api/payment-methods", response_model=List[schemas.PaymentMethod])
def read_payment_methods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.get_payment_methods_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@app.post("/api/payment-methods", response_model=schemas.PaymentMethod)
def create_payment_method_endpoint(
    payment_method: schemas.PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.create_payment_method(db=db, payment_method=payment_method, user_id=current_user.id)

@app.put("/api/payment-methods/{payment_method_id}", response_model=schemas.PaymentMethod)
def update_payment_method_endpoint(
    payment_method_id: int,
    payment_method: schemas.PaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_payment_method = crud.get_payment_method(db, payment_method_id=payment_method_id)
    if db_payment_method is None or db_payment_method.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment Method not found")
    
    return crud.update_payment_method(db=db, payment_method_id=payment_method_id, payment_method=payment_method, user_id=current_user.id)

@app.delete("/api/payment-methods/{payment_method_id}", response_model=schemas.PaymentMethod)
def delete_payment_method_endpoint(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_payment_method = crud.get_payment_method(db, payment_method_id=payment_method_id)
    if db_payment_method is None or db_payment_method.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment Method not found")
    
    return crud.delete_payment_method(db=db, payment_method_id=payment_method_id)

# Account Transaction endpoints
@app.get("/api/account-transactions", response_model=List[schemas.AccountTransaction])
def read_account_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.get_account_transactions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@app.post("/api/account-transactions", response_model=schemas.AccountTransaction)
def create_account_transaction_endpoint(
    account_transaction: schemas.AccountTransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Validate payment method if provided
    if account_transaction.payment_method_id:
        payment_method = crud.get_payment_method(db, payment_method_id=account_transaction.payment_method_id)
        if payment_method is None or payment_method.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Payment Method not found")
    
    # Create the account transaction
    db_account_transaction = crud.create_account_transaction(db=db, account_transaction=account_transaction, user_id=current_user.id)
    
    # Create notification for deposit
    if account_transaction.type == schemas.AccountTransactionType.DEPOSIT:
        notification = schemas.NotificationCreate(
            message=f"Account recharge of ${account_transaction.amount:.2f} completed successfully",
            type=schemas.NotificationType.TRANSACTION_COMPLETE
        )
        crud.create_notification(db=db, notification=notification, user_id=current_user.id)
    
    # Check if balance is low after withdrawal
    if account_transaction.type == schemas.AccountTransactionType.WITHDRAWAL and current_user.current_balance < 10.0:
        notification = schemas.NotificationCreate(
            message="Your account balance is running low. Please recharge to continue using toll services.",
            type=schemas.NotificationType.BALANCE_LOW
        )
        crud.create_notification(db=db, notification=notification, user_id=current_user.id)
    
    return db_account_transaction

# Traffic Data endpoints (for admin use)
@app.post("/api/admin/traffic-data", response_model=schemas.TrafficData)
def create_traffic_data_endpoint(
    traffic_data: schemas.TrafficDataCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # In a real app, you'd check if the user is an admin here
    # Validate the toll plaza exists
    toll_plaza = crud.get_toll_plaza(db, toll_plaza_id=traffic_data.toll_plaza_id)
    if toll_plaza is None:
        raise HTTPException(status_code=404, detail="Toll Plaza not found")
    
    return crud.create_traffic_data(db=db, traffic_data=traffic_data)

# Notification endpoints
@app.get("/api/notifications", response_model=List[schemas.Notification])
def read_notifications(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.get_notifications_by_user(db, user_id=current_user.id, skip=skip, limit=limit, unread_only=unread_only)

@app.put("/api/notifications/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_as_read_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    notification = crud.get_notification(db, notification_id=notification_id)
    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return crud.mark_notification_as_read(db=db, notification_id=notification_id)

@app.put("/api/notifications/mark-all-read")
def mark_all_notifications_as_read_endpoint(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    crud.mark_all_notifications_as_read(db=db, user_id=current_user.id)
    return {"message": "All notifications marked as read"}

# GoogleMaps API integration endpoints

# Models for GoogleMaps API requests
class TrafficRequest(BaseModel):
    location: str

class RouteRequest(BaseModel):
    origin: str
    destination: str

class NearbyTollPlazasRequest(BaseModel):
    location: str
    radius: Optional[int] = 10000  # Default 10km

# Traffic data endpoint
@app.post("/api/maps/traffic")
def get_traffic_data(
    request: TrafficRequest,
    current_user: models.User = Depends(get_current_active_user)
):
    traffic_data = googlemapsapi.get_traffic_details(request.location)
    
    if "error" in traffic_data:
        raise HTTPException(status_code=400, detail=traffic_data["error"])
        
    return traffic_data

# Route information endpoint
@app.post("/api/maps/route")
def get_route_data(
    request: RouteRequest,
    current_user: models.User = Depends(get_current_active_user)
):
    route_data = googlemapsapi.get_route(request.origin, request.destination)
    
    if "error" in route_data:
        raise HTTPException(status_code=400, detail=route_data["error"])
        
    return route_data

# Nearby toll plazas endpoint
@app.post("/api/maps/nearby-toll-plazas")
def get_nearby_toll_plazas_data(
    request: NearbyTollPlazasRequest,
    current_user: models.User = Depends(get_current_active_user)
):
    toll_plazas_data = googlemapsapi.get_nearby_toll_plazas(request.location, request.radius)
    
    if "error" in toll_plazas_data:
        raise HTTPException(status_code=400, detail=toll_plazas_data["error"])
        
    return toll_plazas_data

# Public toll plazas search endpoint (no authentication required)
@app.get("/api/public/toll-plazas/search")
def search_toll_plazas(
    query: str,
    db: Session = Depends(get_db)
):
    # Simple search implementation - in a real app you might use more sophisticated search
    toll_plazas = db.query(models.TollPlaza).filter(
        models.TollPlaza.name.ilike(f"%{query}%") | 
        models.TollPlaza.address.ilike(f"%{query}%") |
        models.TollPlaza.location.ilike(f"%{query}%")
    ).all()
    
    return toll_plazas

# Public toll pricing endpoint (no authentication required)
@app.get("/api/public/toll-plazas/{toll_plaza_id}/pricing")
def get_toll_pricing(
    toll_plaza_id: int,
    vehicle_type: schemas.VehicleType,
    db: Session = Depends(get_db)
):
    toll_plaza = crud.get_toll_plaza(db, toll_plaza_id=toll_plaza_id)
    if toll_plaza is None:
        raise HTTPException(status_code=404, detail="Toll Plaza not found")
    
    # Apply vehicle type multiplier
    multipliers = {
        schemas.VehicleType.CAR: 1.0,
        schemas.VehicleType.MOTORCYCLE: 0.5,
        schemas.VehicleType.TRUCK: 2.0,
        schemas.VehicleType.BUS: 1.5,
        schemas.VehicleType.OTHER: 1.0
    }
    
    vehicle_multiplier = multipliers.get(vehicle_type, 1.0)
    final_price = toll_plaza.current_price * vehicle_multiplier
    
    return {
        "toll_plaza_id": toll_plaza.id,
        "toll_plaza_name": toll_plaza.name,
        "base_price": toll_plaza.base_price,
        "current_price": toll_plaza.current_price,
        "vehicle_type": vehicle_type,
        "vehicle_multiplier": vehicle_multiplier,
        "final_price": final_price,
        "busy_level": toll_plaza.busy_level,
        "estimated_wait_time": toll_plaza.estimated_time
    }

# User statistics endpoint
@app.get("/api/users/me/statistics")
def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Get all transactions for the user
    transactions = crud.get_transactions_by_user(db, user_id=current_user.id)
    
    # Get all vehicles for the user
    vehicles = crud.get_vehicles_by_user(db, user_id=current_user.id)
    
    # Calculate statistics
    total_toll_payments = sum(t.amount for t in transactions if t.transaction_type == "toll payment" and t.status == "completed")
    total_trips = len([t for t in transactions if t.transaction_type == "toll payment" and t.status == "completed"])
    
    # Get most used vehicle
    vehicle_usage = {}
    for t in transactions:
        if t.transaction_type == "toll payment" and t.status == "completed":
            vehicle_usage[t.vehicle_id] = vehicle_usage.get(t.vehicle_id, 0) + 1
    
    most_used_vehicle_id = max(vehicle_usage.items(), key=lambda x: x[1])[0] if vehicle_usage else None
    most_used_vehicle = next((v for v in vehicles if v.id == most_used_vehicle_id), None) if most_used_vehicle_id else None
    
    return {
        "user_id": current_user.id,
        "current_balance": current_user.current_balance,
        "total_vehicles": len(vehicles),
        "active_vehicles": len([v for v in vehicles if v.is_active]),
        "total_toll_payments": total_toll_payments,
        "total_trips": total_trips,
        "average_toll_payment": total_toll_payments / total_trips if total_trips > 0 else 0,
        "most_used_vehicle": {
            "id": most_used_vehicle.id,
            "license_plate": most_used_vehicle.license_plate,
            "make": most_used_vehicle.make,
            "model": most_used_vehicle.model
        } if most_used_vehicle else None
    }

# User monthly transaction report
@app.get("/api/users/me/monthly-report")
def get_monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Get all transactions for the user in the specified month
    transactions = crud.get_transactions_by_user(db, user_id=current_user.id)
    
    # Filter transactions for the specified month
    filtered_transactions = [
        t for t in transactions 
        if t.timestamp.year == year and t.timestamp.month == month
    ]
    
    # Calculate statistics
    total_toll_payments = sum(t.amount for t in filtered_transactions if t.transaction_type == "toll payment" and t.status == "completed")
    total_trips = len([t for t in filtered_transactions if t.transaction_type == "toll payment" and t.status == "completed"])
    
    # Get transactions by day of month
    transactions_by_day = {}
    for t in filtered_transactions:
        if t.transaction_type == "toll payment" and t.status == "completed":
            day = t.timestamp.day
            transactions_by_day[day] = transactions_by_day.get(day, 0) + t.amount
    
    # Format the response
    daily_data = [{"day": day, "amount": amount} for day, amount in transactions_by_day.items()]
    
    return {
        "user_id": current_user.id,
        "year": year,
        "month": month,
        "total_toll_payments": total_toll_payments,
        "total_trips": total_trips,
        "average_toll_payment": total_toll_payments / total_trips if total_trips > 0 else 0,
        "daily_data": daily_data
    }

# Admin endpoint to export database
@app.get("/api/admin/export-data")
def export_database_endpoint(current_user: models.User = Depends(get_current_active_user)):
    # In a real app, you'd check if the user is an admin here
    result = export_database_to_sql()
    return {"message": result}
