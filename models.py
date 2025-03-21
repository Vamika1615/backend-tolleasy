from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from utils import get_ist_now

Base = declarative_base()

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"

class TransactionStatus(str, enum.Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"

class TransactionType(str, enum.Enum):
    TOLL_PAYMENT = "toll payment"
    ACCOUNT_RECHARGE = "account recharge"

class VehicleType(str, enum.Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    BUS = "bus"
    OTHER = "other"

class BusyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AccountTransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"

class NotificationType(str, enum.Enum):
    BALANCE_LOW = "balance_low"
    TRANSACTION_COMPLETE = "transaction_complete"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    GENERAL = "general"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)
    phone_number = Column(String)
    address = Column(String)
    current_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=get_ist_now)
    updated_at = Column(DateTime, default=get_ist_now, onupdate=get_ist_now)
    subscription_plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    subscription_status = Column(String, default=SubscriptionStatus.ACTIVE)
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    account_transactions = relationship("AccountTransaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    plan = relationship("Plan", back_populates="users")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    license_plate = Column(String, unique=True, index=True)
    vehicle_type = Column(String)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    color = Column(String)
    transponder_id = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_ist_now)
    updated_at = Column(DateTime, default=get_ist_now, onupdate=get_ist_now)

    # Relationships
    user = relationship("User", back_populates="vehicles")
    transactions = relationship("Transaction", back_populates="vehicle")

class TollPlaza(Base):
    __tablename__ = "toll_plazas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)  # Geographical coordinates
    address = Column(String)
    base_price = Column(Float)
    current_price = Column(Float)
    busy_level = Column(String, default=BusyLevel.LOW)
    estimated_time = Column(Integer)  # Time in minutes
    vehicles_per_hour = Column(Integer)

    # Relationships
    transactions = relationship("Transaction", back_populates="toll_plaza")
    traffic_data = relationship("TrafficData", back_populates="toll_plaza")

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)  # Monthly price
    annual_price = Column(Float)
    max_vehicles = Column(Integer)
    features = Column(JSON)
    is_active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", back_populates="plan")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    toll_plaza_id = Column(Integer, ForeignKey("toll_plazas.id"))
    amount = Column(Float)
    timestamp = Column(DateTime, default=get_ist_now)
    status = Column(String, default=TransactionStatus.PENDING)
    transaction_type = Column(String)
    payment_method = Column(String, nullable=True)
    reference_id = Column(String, unique=True, index=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    vehicle = relationship("Vehicle", back_populates="transactions")
    toll_plaza = relationship("TollPlaza", back_populates="transactions")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    payment_type = Column(String)
    payment_details = Column(String)  # Encrypted
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_ist_now)
    updated_at = Column(DateTime, default=get_ist_now, onupdate=get_ist_now)

    # Relationships
    user = relationship("User", back_populates="payment_methods")
    account_transactions = relationship("AccountTransaction", back_populates="payment_method")

class AccountTransaction(Base):
    __tablename__ = "account_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    type = Column(String)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    status = Column(String)
    timestamp = Column(DateTime, default=get_ist_now)
    reference_id = Column(String, unique=True, index=True)

    # Relationships
    user = relationship("User", back_populates="account_transactions")
    payment_method = relationship("PaymentMethod", back_populates="account_transactions")

class TrafficData(Base):
    __tablename__ = "traffic_data"

    id = Column(Integer, primary_key=True, index=True)
    toll_plaza_id = Column(Integer, ForeignKey("toll_plazas.id"))
    timestamp = Column(DateTime, default=get_ist_now)
    vehicle_count = Column(Integer)
    average_wait_time = Column(Integer)  # Time in minutes
    price_multiplier = Column(Float)

    # Relationships
    toll_plaza = relationship("TollPlaza", back_populates="traffic_data")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    type = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_ist_now)

    # Relationships
    user = relationship("User", back_populates="notifications") 