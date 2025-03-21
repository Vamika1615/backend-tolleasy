from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

import crud
import models
import schemas
from database import get_db, init_db
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

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
