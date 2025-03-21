from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite in-memory database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine for SQLite in-memory database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base from models
from models import Base

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    # Import all models to ensure they are registered with the Base metadata
    from models import User, Vehicle, TollPlaza, Plan, Transaction, PaymentMethod, AccountTransaction, TrafficData, Notification
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize with some default data
    db = SessionLocal()
    try:
        # Check if we need to seed initial data
        if db.query(Plan).count() == 0:
            seed_initial_data(db)
    finally:
        db.close()

# Seed initial data
def seed_initial_data(db):
    from models import Plan
    import json
    
    # Create default plans
    basic_plan = Plan(
        name="Basic",
        price=9.99,
        annual_price=99.99,
        max_vehicles=2,
        features=json.dumps({
            "free_passes": 5,
            "discount": 0,
            "priority_support": False
        }),
        is_active=True
    )
    
    premium_plan = Plan(
        name="Premium",
        price=19.99,
        annual_price=199.99,
        max_vehicles=5,
        features=json.dumps({
            "free_passes": 10,
            "discount": 5,
            "priority_support": True
        }),
        is_active=True
    )
    
    business_plan = Plan(
        name="Business",
        price=49.99,
        annual_price=499.99,
        max_vehicles=10,
        features=json.dumps({
            "free_passes": 20,
            "discount": 10,
            "priority_support": True,
            "dedicated_manager": True
        }),
        is_active=True
    )
    
    db.add(basic_plan)
    db.add(premium_plan)
    db.add(business_plan)
    db.commit() 