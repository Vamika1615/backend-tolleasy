import json
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_password_hash
from database import SessionLocal
from utils import get_ist_now

def create_dummy_data():
    """
    Populate the database with dummy data for testing purposes
    """
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(models.User).count() > 0:
            print("Database already contains data. Skipping dummy data creation.")
            return
        
        # Create subscription plans
        print("Creating subscription plans...")
        basic_plan = models.Plan(
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
        
        premium_plan = models.Plan(
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
        
        business_plan = models.Plan(
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
        
        # Create toll plazas
        print("Creating toll plazas...")
        toll_plazas = [
            models.TollPlaza(
                name="City Center Toll Plaza",
                location="12.9716,77.5946",  # Bangalore
                address="MG Road, Bangalore",
                base_price=50.0,
                current_price=60.0,
                busy_level=models.BusyLevel.MEDIUM,
                estimated_time=5,
                vehicles_per_hour=120
            ),
            models.TollPlaza(
                name="Highway Express Toll",
                location="28.7041,77.1025",  # Delhi
                address="NH-8, Delhi",
                base_price=75.0,
                current_price=85.0,
                busy_level=models.BusyLevel.HIGH,
                estimated_time=10,
                vehicles_per_hour=200
            ),
            models.TollPlaza(
                name="Coastal Road Toll",
                location="19.0760,72.8777",  # Mumbai
                address="Marine Drive, Mumbai",
                base_price=100.0,
                current_price=120.0,
                busy_level=models.BusyLevel.LOW,
                estimated_time=3,
                vehicles_per_hour=80
            ),
            models.TollPlaza(
                name="Eastern Expressway Toll",
                location="22.5726,88.3639",  # Kolkata
                address="Eastern Expressway, Kolkata",
                base_price=65.0,
                current_price=70.0,
                busy_level=models.BusyLevel.MEDIUM,
                estimated_time=7,
                vehicles_per_hour=150
            ),
            models.TollPlaza(
                name="Outer Ring Toll Plaza",
                location="13.0827,80.2707",  # Chennai
                address="Outer Ring Road, Chennai",
                base_price=80.0,
                current_price=90.0,
                busy_level=models.BusyLevel.LOW,
                estimated_time=4,
                vehicles_per_hour=90
            )
        ]
        
        for toll_plaza in toll_plazas:
            db.add(toll_plaza)
        db.commit()
        
        # Create 20 users
        print("Creating 20 users with vehicles, payment methods, and transactions...")
        users = []
        
        first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Atharva", "Krishna", "Ishaan", 
                       "Aanya", "Aadhya", "Sai", "Divya", "Ananya", "Anika", "Riya", "Diya", "Myra", "Sara"]
        
        last_names = ["Sharma", "Singh", "Kumar", "Patel", "Shah", "Gupta", "Jain", "Mishra", "Reddy", "Das", 
                      "Nair", "Menon", "Rao", "Iyer", "Mehta", "Joshi", "Pandey", "Banerjee", "Bose", "Chatterjee"]
        
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com"]
        
        vehicle_makes = ["Maruti", "Hyundai", "Tata", "Mahindra", "Toyota", "Honda", "Kia", "MG", "Ford", "Renault"]
        vehicle_models = ["Swift", "i20", "Nexon", "XUV300", "Innova", "City", "Seltos", "Hector", "EcoSport", "Kwid"]
        colors = ["Red", "Blue", "Black", "White", "Silver", "Grey", "Green", "Yellow", "Orange", "Brown"]
        
        # Payment types
        payment_types = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet"]
        
        plans = [basic_plan, premium_plan, business_plan, None]
        plan_weights = [0.4, 0.3, 0.2, 0.1]  # 40% basic, 30% premium, 20% business, 10% no plan
        
        for i in range(1, 21):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}"
            phone = f"+91{random.randint(7000000000, 9999999999)}"
            
            # Assign a plan based on weighted probabilities
            subscription_plan = random.choices(plans, weights=plan_weights)[0]
            
            # Calculate subscription dates if plan is assigned
            if subscription_plan:
                subscription_start_date = get_ist_now() - timedelta(days=random.randint(1, 180))
                subscription_end_date = subscription_start_date + timedelta(days=365)
            else:
                subscription_start_date = None
                subscription_end_date = None
            
            # Create user
            user = models.User(
                email=email,
                password_hash=get_password_hash("password123"),  # Same password for all dummy users
                name=f"{first_name} {last_name}",
                phone_number=phone,
                address=f"{random.randint(1, 999)}, {random.choice(['Main Street', 'Park Avenue', 'MG Road', 'Ring Road', 'Beach Road'])}, {random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune'])}",
                current_balance=random.uniform(200, 5000),
                created_at=get_ist_now() - timedelta(days=random.randint(1, 365)),
                updated_at=get_ist_now(),
                subscription_plan_id=subscription_plan.id if subscription_plan else None,
                subscription_status=models.SubscriptionStatus.ACTIVE if subscription_plan else models.SubscriptionStatus.EXPIRED,
                subscription_start_date=subscription_start_date,
                subscription_end_date=subscription_end_date
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            users.append(user)
            
            # Create 1-3 vehicles for each user
            num_vehicles = min(random.randint(1, 3), subscription_plan.max_vehicles if subscription_plan else 1)
            for j in range(num_vehicles):
                vehicle_type = random.choice(list(models.VehicleType))
                make = random.choice(vehicle_makes)
                model = random.choice(vehicle_models)
                year = random.randint(2010, 2024)
                color = random.choice(colors)
                
                # Create license plate (format: AB12CD3456)
                license_plate = f"{chr(65 + random.randint(0, 25))}{chr(65 + random.randint(0, 25))}{random.randint(10, 99)}{chr(65 + random.randint(0, 25))}{chr(65 + random.randint(0, 25))}{random.randint(1000, 9999)}"
                
                vehicle = models.Vehicle(
                    user_id=user.id,
                    license_plate=license_plate,
                    vehicle_type=vehicle_type,
                    make=make,
                    model=model,
                    year=year,
                    color=color,
                    transponder_id=f"T-{uuid.uuid4().hex[:8].upper()}",
                    is_active=random.random() > 0.1,  # 90% chance of being active
                    created_at=get_ist_now() - timedelta(days=random.randint(1, 365)),
                    updated_at=get_ist_now()
                )
                
                db.add(vehicle)
                db.commit()
                db.refresh(vehicle)
                
                # Create 0-5 transactions for each vehicle
                num_transactions = random.randint(0, 5)
                for k in range(num_transactions):
                    toll_plaza = random.choice(toll_plazas)
                    amount = toll_plaza.current_price * (1.5 if vehicle_type == models.VehicleType.TRUCK else 
                                                         1.3 if vehicle_type == models.VehicleType.BUS else 
                                                         0.7 if vehicle_type == models.VehicleType.MOTORCYCLE else 1.0)
                    
                    transaction = models.Transaction(
                        user_id=user.id,
                        vehicle_id=vehicle.id,
                        toll_plaza_id=toll_plaza.id,
                        amount=amount,
                        timestamp=get_ist_now() - timedelta(days=random.randint(1, 90), hours=random.randint(1, 24)),
                        status=models.TransactionStatus.COMPLETED,
                        transaction_type=models.TransactionType.TOLL_PAYMENT,
                        payment_method="Transponder",
                        reference_id=str(uuid.uuid4())
                    )
                    
                    db.add(transaction)
                    
                    # Add notifications for some transactions
                    if random.random() > 0.5:  # 50% chance
                        notification = models.Notification(
                            user_id=user.id,
                            message=f"Toll payment of ₹{amount:.2f} completed successfully at {toll_plaza.name}",
                            type=models.NotificationType.TRANSACTION_COMPLETE,
                            is_read=random.random() > 0.3,  # 70% chance of being read
                            created_at=transaction.timestamp + timedelta(seconds=30)
                        )
                        db.add(notification)
            
            # Create 0-2 payment methods for each user
            num_payment_methods = random.randint(0, 2)
            for j in range(num_payment_methods):
                payment_type = random.choice(payment_types)
                
                if payment_type == "Credit Card" or payment_type == "Debit Card":
                    # Mask card numbers for security
                    payment_details = f"XXXX-XXXX-XXXX-{random.randint(1000, 9999)}"
                elif payment_type == "UPI":
                    payment_details = f"{user.email.split('@')[0]}@upi"
                else:
                    payment_details = f"{payment_type} - {user.name}"
                
                payment_method = models.PaymentMethod(
                    user_id=user.id,
                    payment_type=payment_type,
                    payment_details=payment_details,
                    is_default=j == 0,  # First payment method is default
                    created_at=get_ist_now() - timedelta(days=random.randint(1, 180)),
                    updated_at=get_ist_now()
                )
                
                db.add(payment_method)
                db.commit()
                db.refresh(payment_method)
                
                # Create 0-3 account transactions for each payment method
                num_account_transactions = random.randint(0, 3)
                for k in range(num_account_transactions):
                    transaction_type = random.choice(list(models.AccountTransactionType))
                    amount = random.uniform(100, 1000)
                    
                    account_transaction = models.AccountTransaction(
                        user_id=user.id,
                        amount=amount,
                        type=transaction_type,
                        payment_method_id=payment_method.id,
                        status="completed",
                        timestamp=get_ist_now() - timedelta(days=random.randint(1, 90), hours=random.randint(1, 24)),
                        reference_id=str(uuid.uuid4())
                    )
                    
                    db.add(account_transaction)
                    
                    # Add notifications for some account transactions
                    if random.random() > 0.5:  # 50% chance
                        message = f"Account {'deposit' if transaction_type == models.AccountTransactionType.DEPOSIT else 'withdrawal'} of ₹{amount:.2f} completed successfully"
                        notification = models.Notification(
                            user_id=user.id,
                            message=message,
                            type=models.NotificationType.TRANSACTION_COMPLETE,
                            is_read=random.random() > 0.3,  # 70% chance of being read
                            created_at=account_transaction.timestamp + timedelta(seconds=30)
                        )
                        db.add(notification)
            
            # Add some random notifications for each user
            num_notifications = random.randint(1, 5)
            for j in range(num_notifications):
                notification_type = random.choice(list(models.NotificationType))
                
                if notification_type == models.NotificationType.BALANCE_LOW:
                    message = "Your account balance is running low. Please recharge to continue using toll services."
                elif notification_type == models.NotificationType.SUBSCRIPTION_EXPIRING:
                    days_left = random.randint(1, 10)
                    message = f"Your subscription is expiring in {days_left} {'day' if days_left == 1 else 'days'}. Renew now to continue enjoying benefits."
                else:
                    message = "Thank you for using TollEasy! Drive safely."
                
                notification = models.Notification(
                    user_id=user.id,
                    message=message,
                    type=notification_type,
                    is_read=random.random() > 0.5,  # 50% chance of being read
                    created_at=get_ist_now() - timedelta(days=random.randint(1, 30), hours=random.randint(1, 24))
                )
                
                db.add(notification)
            
            db.commit()
        
        print("Successfully created dummy data!")
        return "Dummy data created successfully"
    except Exception as e:
        db.rollback()
        print(f"Error creating dummy data: {e}")
        return f"Error creating dummy data: {e}"
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_data() 