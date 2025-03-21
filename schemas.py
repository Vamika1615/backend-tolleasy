from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"

class TransactionStatus(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"

class TransactionType(str, Enum):
    TOLL_PAYMENT = "toll payment"
    ACCOUNT_RECHARGE = "account recharge"

class VehicleType(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    BUS = "bus"
    OTHER = "other"

class BusyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AccountTransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"

class NotificationType(str, Enum):
    BALANCE_LOW = "balance_low"
    TRANSACTION_COMPLETE = "transaction_complete"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    GENERAL = "general"

# Base schema models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    current_balance: Optional[float] = None
    subscription_plan_id: Optional[int] = None
    subscription_status: Optional[SubscriptionStatus] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None

class UserInDB(UserBase):
    id: int
    current_balance: float
    created_at: datetime
    updated_at: datetime
    subscription_plan_id: Optional[int] = None
    subscription_status: SubscriptionStatus
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

class VehicleBase(BaseModel):
    license_plate: str
    vehicle_type: VehicleType
    make: str
    model: str
    year: int
    color: str
    transponder_id: str
    is_active: bool = True

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    transponder_id: Optional[str] = None
    is_active: Optional[bool] = None

class VehicleInDB(VehicleBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Vehicle(VehicleInDB):
    pass

class TollPlazaBase(BaseModel):
    name: str
    location: str
    address: str
    base_price: float
    current_price: float
    busy_level: BusyLevel = BusyLevel.LOW
    estimated_time: int
    vehicles_per_hour: int

class TollPlazaCreate(TollPlazaBase):
    pass

class TollPlazaUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    base_price: Optional[float] = None
    current_price: Optional[float] = None
    busy_level: Optional[BusyLevel] = None
    estimated_time: Optional[int] = None
    vehicles_per_hour: Optional[int] = None

class TollPlazaInDB(TollPlazaBase):
    id: int

    class Config:
        orm_mode = True

class TollPlaza(TollPlazaInDB):
    pass

class PlanBase(BaseModel):
    name: str
    price: float
    annual_price: float
    max_vehicles: int
    features: Dict[str, Any]
    is_active: bool = True

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    annual_price: Optional[float] = None
    max_vehicles: Optional[int] = None
    features: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PlanInDB(PlanBase):
    id: int

    class Config:
        orm_mode = True

class Plan(PlanInDB):
    pass

class TransactionBase(BaseModel):
    vehicle_id: int
    toll_plaza_id: int
    amount: float
    transaction_type: TransactionType
    payment_method: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    payment_method: Optional[str] = None

class TransactionInDB(TransactionBase):
    id: int
    user_id: int
    timestamp: datetime
    status: TransactionStatus
    reference_id: str

    class Config:
        orm_mode = True

class Transaction(TransactionInDB):
    pass

class PaymentMethodBase(BaseModel):
    payment_type: str
    payment_details: str
    is_default: bool = False

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodUpdate(BaseModel):
    payment_type: Optional[str] = None
    payment_details: Optional[str] = None
    is_default: Optional[bool] = None

class PaymentMethodInDB(PaymentMethodBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PaymentMethod(PaymentMethodInDB):
    pass

class AccountTransactionBase(BaseModel):
    amount: float
    type: AccountTransactionType
    payment_method_id: Optional[int] = None

class AccountTransactionCreate(AccountTransactionBase):
    pass

class AccountTransactionUpdate(BaseModel):
    status: Optional[str] = None

class AccountTransactionInDB(AccountTransactionBase):
    id: int
    user_id: int
    status: str
    timestamp: datetime
    reference_id: str

    class Config:
        orm_mode = True

class AccountTransaction(AccountTransactionInDB):
    pass

class TrafficDataBase(BaseModel):
    toll_plaza_id: int
    vehicle_count: int
    average_wait_time: int
    price_multiplier: float

class TrafficDataCreate(TrafficDataBase):
    pass

class TrafficDataUpdate(BaseModel):
    vehicle_count: Optional[int] = None
    average_wait_time: Optional[int] = None
    price_multiplier: Optional[float] = None

class TrafficDataInDB(TrafficDataBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class TrafficData(TrafficDataInDB):
    pass

class NotificationBase(BaseModel):
    message: str
    type: NotificationType
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationInDB(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Notification(NotificationInDB):
    pass

# Token schemas for authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 