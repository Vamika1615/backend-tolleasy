from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import json

import models
import schemas
from auth import get_password_hash
from utils import get_ist_now

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        name=user.name,
        phone_number=user.phone_number,
        address=user.address,
        current_balance=0.0,
        subscription_status=models.SubscriptionStatus.ACTIVE
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db_user.updated_at = get_ist_now()
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

# Vehicle CRUD operations
def get_vehicles_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Vehicle).filter(models.Vehicle.user_id == user_id).offset(skip).limit(limit).all()

def get_vehicle(db: Session, vehicle_id: int):
    return db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, user_id: int):
    db_vehicle = models.Vehicle(
        **vehicle.dict(),
        user_id=user_id
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, vehicle_id: int, vehicle: schemas.VehicleUpdate):
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        return None
    
    update_data = vehicle.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vehicle, key, value)
    
    db_vehicle.updated_at = get_ist_now()
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, vehicle_id: int):
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        return None
    db.delete(db_vehicle)
    db.commit()
    return db_vehicle

# TollPlaza CRUD operations
def get_toll_plazas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TollPlaza).offset(skip).limit(limit).all()

def get_toll_plaza(db: Session, toll_plaza_id: int):
    return db.query(models.TollPlaza).filter(models.TollPlaza.id == toll_plaza_id).first()

def create_toll_plaza(db: Session, toll_plaza: schemas.TollPlazaCreate):
    db_toll_plaza = models.TollPlaza(**toll_plaza.dict())
    db.add(db_toll_plaza)
    db.commit()
    db.refresh(db_toll_plaza)
    return db_toll_plaza

def update_toll_plaza(db: Session, toll_plaza_id: int, toll_plaza: schemas.TollPlazaUpdate):
    db_toll_plaza = db.query(models.TollPlaza).filter(models.TollPlaza.id == toll_plaza_id).first()
    if not db_toll_plaza:
        return None
    
    update_data = toll_plaza.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_toll_plaza, key, value)
    
    db.commit()
    db.refresh(db_toll_plaza)
    return db_toll_plaza

def delete_toll_plaza(db: Session, toll_plaza_id: int):
    db_toll_plaza = db.query(models.TollPlaza).filter(models.TollPlaza.id == toll_plaza_id).first()
    if not db_toll_plaza:
        return None
    db.delete(db_toll_plaza)
    db.commit()
    return db_toll_plaza

# Plan CRUD operations
def get_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Plan).filter(models.Plan.is_active == True).offset(skip).limit(limit).all()

def get_plan(db: Session, plan_id: int):
    return db.query(models.Plan).filter(models.Plan.id == plan_id).first()

def create_plan(db: Session, plan: schemas.PlanCreate):
    # Convert features dict to JSON string
    if isinstance(plan.features, dict):
        features_json = json.dumps(plan.features)
    else:
        features_json = plan.features
    
    db_plan = models.Plan(
        name=plan.name,
        price=plan.price,
        annual_price=plan.annual_price,
        max_vehicles=plan.max_vehicles,
        features=features_json,
        is_active=plan.is_active
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id: int, plan: schemas.PlanUpdate):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        return None
    
    update_data = plan.dict(exclude_unset=True)
    
    # Convert features dict to JSON string if it exists
    if "features" in update_data and isinstance(update_data["features"], dict):
        update_data["features"] = json.dumps(update_data["features"])
    
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: int):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        return None
    db.delete(db_plan)
    db.commit()
    return db_plan

# Transaction CRUD operations
def get_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    # Generate a unique reference ID
    reference_id = str(uuid.uuid4())
    
    db_transaction = models.Transaction(
        **transaction.dict(),
        user_id=user_id,
        status=models.TransactionStatus.PENDING,
        reference_id=reference_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Update user balance
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if transaction.transaction_type == models.TransactionType.TOLL_PAYMENT:
        db_user.current_balance -= transaction.amount
    elif transaction.transaction_type == models.TransactionType.ACCOUNT_RECHARGE:
        db_user.current_balance += transaction.amount
    
    db.commit()
    
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_transaction:
        return None
    
    update_data = transaction.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# PaymentMethod CRUD operations
def get_payment_methods_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.PaymentMethod).filter(models.PaymentMethod.user_id == user_id).offset(skip).limit(limit).all()

def get_payment_method(db: Session, payment_method_id: int):
    return db.query(models.PaymentMethod).filter(models.PaymentMethod.id == payment_method_id).first()

def create_payment_method(db: Session, payment_method: schemas.PaymentMethodCreate, user_id: int):
    db_payment_method = models.PaymentMethod(
        **payment_method.dict(),
        user_id=user_id
    )
    
    # If this is set as default, unset other default payment methods
    if payment_method.is_default:
        db.query(models.PaymentMethod).filter(
            models.PaymentMethod.user_id == user_id,
            models.PaymentMethod.is_default == True
        ).update({models.PaymentMethod.is_default: False})
    
    db.add(db_payment_method)
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

def update_payment_method(db: Session, payment_method_id: int, payment_method: schemas.PaymentMethodUpdate, user_id: int):
    db_payment_method = db.query(models.PaymentMethod).filter(models.PaymentMethod.id == payment_method_id).first()
    if not db_payment_method:
        return None
    
    update_data = payment_method.dict(exclude_unset=True)
    
    # If this is being set as default, unset other default payment methods
    if update_data.get("is_default"):
        db.query(models.PaymentMethod).filter(
            models.PaymentMethod.user_id == user_id,
            models.PaymentMethod.is_default == True
        ).update({models.PaymentMethod.is_default: False})
    
    for key, value in update_data.items():
        setattr(db_payment_method, key, value)
    
    db_payment_method.updated_at = get_ist_now()
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

def delete_payment_method(db: Session, payment_method_id: int):
    db_payment_method = db.query(models.PaymentMethod).filter(models.PaymentMethod.id == payment_method_id).first()
    if not db_payment_method:
        return None
    db.delete(db_payment_method)
    db.commit()
    return db_payment_method

# AccountTransaction CRUD operations
def get_account_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.AccountTransaction).filter(models.AccountTransaction.user_id == user_id).offset(skip).limit(limit).all()

def get_account_transaction(db: Session, account_transaction_id: int):
    return db.query(models.AccountTransaction).filter(models.AccountTransaction.id == account_transaction_id).first()

def create_account_transaction(db: Session, account_transaction: schemas.AccountTransactionCreate, user_id: int):
    # Generate a unique reference ID
    reference_id = str(uuid.uuid4())
    
    db_account_transaction = models.AccountTransaction(
        **account_transaction.dict(),
        user_id=user_id,
        status="completed",
        reference_id=reference_id
    )
    db.add(db_account_transaction)
    db.commit()
    db.refresh(db_account_transaction)
    
    # Update user balance
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if account_transaction.type == models.AccountTransactionType.DEPOSIT:
        db_user.current_balance += account_transaction.amount
    elif account_transaction.type == models.AccountTransactionType.WITHDRAWAL:
        db_user.current_balance -= account_transaction.amount
    elif account_transaction.type == models.AccountTransactionType.REFUND:
        db_user.current_balance += account_transaction.amount
    
    db.commit()
    
    return db_account_transaction

# TrafficData CRUD operations
def get_traffic_data_by_toll_plaza(db: Session, toll_plaza_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.TrafficData).filter(models.TrafficData.toll_plaza_id == toll_plaza_id).offset(skip).limit(limit).all()

def create_traffic_data(db: Session, traffic_data: schemas.TrafficDataCreate):
    db_traffic_data = models.TrafficData(**traffic_data.dict())
    db.add(db_traffic_data)
    db.commit()
    db.refresh(db_traffic_data)
    
    # Update toll plaza busy level and price based on traffic data
    db_toll_plaza = db.query(models.TollPlaza).filter(models.TollPlaza.id == traffic_data.toll_plaza_id).first()
    
    # Update busy level based on vehicle count
    if traffic_data.vehicle_count < 50:
        db_toll_plaza.busy_level = models.BusyLevel.LOW
    elif traffic_data.vehicle_count < 100:
        db_toll_plaza.busy_level = models.BusyLevel.MEDIUM
    else:
        db_toll_plaza.busy_level = models.BusyLevel.HIGH
    
    # Update current price based on price multiplier
    db_toll_plaza.current_price = db_toll_plaza.base_price * traffic_data.price_multiplier
    
    # Update estimated time
    db_toll_plaza.estimated_time = traffic_data.average_wait_time
    
    # Update vehicles per hour
    db_toll_plaza.vehicles_per_hour = traffic_data.vehicle_count
    
    db.commit()
    
    return db_traffic_data

# Notification CRUD operations
def get_notifications_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100, unread_only: bool = False):
    query = db.query(models.Notification).filter(models.Notification.user_id == user_id)
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
    return query.order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()

def get_notification(db: Session, notification_id: int):
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()

def create_notification(db: Session, notification: schemas.NotificationCreate, user_id: int):
    db_notification = models.Notification(
        **notification.dict(),
        user_id=user_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def mark_notification_as_read(db: Session, notification_id: int):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not db_notification:
        return None
    
    db_notification.is_read = True
    db.commit()
    db.refresh(db_notification)
    return db_notification

def mark_all_notifications_as_read(db: Session, user_id: int):
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).update({models.Notification.is_read: True})
    db.commit()
    return True 