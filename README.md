# TollEasy Backend API

A robust FastAPI backend for a toll management system with an in-memory SQLite database.

## Features

- User management with JWT authentication
- Vehicle registration and management
- Toll plaza information
- Transaction processing for toll payments
- Account balance management
- Payment method handling
- Subscription plans
- Traffic data and dynamic pricing
- Notification system
- Indian Standard Time (IST) time zone support

## Database Schema

The application uses an in-memory SQLite database with the following tables:

- Users: Manage user accounts, balances, and subscription plans
- Vehicles: Store vehicle information linked to users
- Transactions: Record toll payments and account recharges
- TollPlazas: Information about toll locations, prices, and traffic conditions
- Plans: Subscription plans with features and pricing
- PaymentMethods: User payment methods
- AccountTransactions: Account balance changes
- TrafficData: Traffic statistics for toll plazas
- Notifications: User notifications

## Getting Started

### Prerequisites

- Python 3.11+ is required (avoid Python 3.13 due to compatibility issues)
- pip for package installation

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/tolleasy-backend.git
   cd tolleasy-backend
   ```

2. Run the installation script to set up the virtual environment and dependencies:
   ```
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

### Running the Application

Start the FastAPI server:

```
chmod +x run.sh
./run.sh
```

The API will be available at http://localhost:8000

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

The API provides the following endpoints:

### Authentication
- `POST /api/token`: Get JWT token by providing username and password

### Users
- `POST /api/users`: Register a new user
- `GET /api/users/me`: Get current user information
- `PUT /api/users/me`: Update current user information

### Vehicles
- `GET /api/vehicles`: List user's vehicles
- `POST /api/vehicles`: Register a new vehicle
- `GET /api/vehicles/{vehicle_id}`: Get a specific vehicle
- `PUT /api/vehicles/{vehicle_id}`: Update a vehicle
- `DELETE /api/vehicles/{vehicle_id}`: Delete a vehicle

### Toll Plazas
- `GET /api/toll-plazas`: List all toll plazas
- `GET /api/toll-plazas/{toll_plaza_id}`: Get a specific toll plaza

### Plans
- `GET /api/plans`: List all subscription plans
- `GET /api/plans/{plan_id}`: Get a specific plan

### Transactions
- `GET /api/transactions`: List user's transactions
- `POST /api/transactions`: Create a new transaction
- `GET /api/transactions/{transaction_id}`: Get a specific transaction

### Payment Methods
- `GET /api/payment-methods`: List user's payment methods
- `POST /api/payment-methods`: Add a new payment method
- `PUT /api/payment-methods/{payment_method_id}`: Update a payment method
- `DELETE /api/payment-methods/{payment_method_id}`: Delete a payment method

### Account Transactions
- `GET /api/account-transactions`: List user's account transactions
- `POST /api/account-transactions`: Create a new account transaction

### Notifications
- `GET /api/notifications`: List user's notifications
- `PUT /api/notifications/{notification_id}/read`: Mark a notification as read
- `PUT /api/notifications/mark-all-read`: Mark all notifications as read

## Admin Endpoints

These endpoints would typically be restricted to admin users:

- `POST /api/admin/toll-plazas`: Create a toll plaza
- `PUT /api/admin/toll-plazas/{toll_plaza_id}`: Update a toll plaza
- `POST /api/admin/plans`: Create a subscription plan
- `PUT /api/admin/plans/{plan_id}`: Update a subscription plan
- `POST /api/admin/traffic-data`: Submit traffic data for a toll plaza

## Technical Notes

- All timestamps use Indian Standard Time (IST) instead of UTC
- In-memory SQLite database (data is lost when the server stops)
- JWT authentication with token expiration
- Password hashing with bcrypt 