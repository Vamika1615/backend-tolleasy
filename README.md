# TollEasy Backend

This is the backend API for the TollEasy application, a toll management system that helps users with toll payments, route planning, and traffic management.

## Features

- User authentication and management
- Vehicle registration and management
- Toll plaza information and pricing
- Transaction tracking and history
- Payment method management
- Account balance and recharge functionality
- Google Maps API integration for traffic and toll plaza data
- User statistics and reports
- Notifications system
- Built-in dummy data generation for testing

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Vamika1615/backend-tolleasy.git
cd backend-tolleasy
```

2. Install dependencies:
```bash
./install_dependencies.sh
```

3. Configure environment variables:
Edit the `.env` file with your configuration:
```
DATABASE_URL="sqlite:///:memory:"
JWT_SECRET_KEY="your_secure_secret_key"
GOOGLE_MAPS_API_KEY="your_google_maps_api_key_here"
```

4. Start the server:
```bash
./run.sh
```

The API will be available at http://localhost:8000. API documentation will be available at http://localhost:8000/docs or http://localhost:8000/redoc.

## Dummy Data

The application automatically generates dummy data for testing purposes when it first starts up. This includes:

- 20 random users with realistic Indian names and contact information
- 1-3 vehicles per user based on their subscription plan
- 5 toll plazas across major Indian cities
- Random transactions, payment methods, and notifications
- 3 subscription plans (Basic, Premium, Business)

All dummy users are created with the same password: `password123`

Dummy users follow the format: `firstname.lastname###@domain.com` (where ### is a random number)

Example credentials for testing:
- Email: `aarav.sharma123@gmail.com` (actual emails will vary)
- Password: `password123`

For more details, see the `dummy_users.txt` file.

## API Endpoints

### Authentication
- `POST /api/token`: Login to get access token

### User Management
- `POST /api/users`: Register a new user
- `GET /api/users/me`: Get current user profile
- `PUT /api/users/me`: Update current user profile
- `GET /api/users/me/statistics`: Get user statistics
- `GET /api/users/me/monthly-report`: Get monthly transaction report

### Vehicle Management
- `GET /api/vehicles`: List user's vehicles
- `POST /api/vehicles`: Add a vehicle
- `GET /api/vehicles/{vehicle_id}`: Get vehicle details
- `PUT /api/vehicles/{vehicle_id}`: Update vehicle
- `DELETE /api/vehicles/{vehicle_id}`: Delete vehicle

### Toll Plaza Information
- `GET /api/toll-plazas`: List toll plazas
- `GET /api/toll-plazas/{toll_plaza_id}`: Get toll plaza details
- `GET /api/public/toll-plazas/search`: Search toll plazas
- `GET /api/public/toll-plazas/{toll_plaza_id}/pricing`: Get toll pricing

### Transaction Management
- `GET /api/transactions`: List user's transactions
- `POST /api/transactions`: Create a transaction
- `GET /api/transactions/{transaction_id}`: Get transaction details

### Payment Methods
- `GET /api/payment-methods`: List user's payment methods
- `POST /api/payment-methods`: Add a payment method
- `PUT /api/payment-methods/{payment_method_id}`: Update payment method
- `DELETE /api/payment-methods/{payment_method_id}`: Delete payment method

### Account Transactions
- `GET /api/account-transactions`: List user's account transactions
- `POST /api/account-transactions`: Create account transaction (deposit/withdrawal)

### Notifications
- `GET /api/notifications`: List user's notifications
- `PUT /api/notifications/{notification_id}/read`: Mark notification as read
- `PUT /api/notifications/mark-all-read`: Mark all notifications as read

### Plans
- `GET /api/plans`: List subscription plans
- `GET /api/plans/{plan_id}`: Get plan details

### Google Maps Integration
- `POST /api/maps/traffic`: Get traffic information for a location
- `POST /api/maps/route`: Get route information between two locations
- `POST /api/maps/nearby-toll-plazas`: Find toll plazas near a location

### Admin Endpoints
- `POST /api/admin/toll-plazas`: Create toll plaza
- `PUT /api/admin/toll-plazas/{toll_plaza_id}`: Update toll plaza
- `POST /api/admin/plans`: Create subscription plan
- `PUT /api/admin/plans/{plan_id}`: Update subscription plan
- `POST /api/admin/traffic-data`: Add traffic data

## Database Schema

The application uses an SQLite database with the following models:
- User: Stores user information and account details
- Vehicle: User's registered vehicles
- TollPlaza: Information about toll plazas
- Plan: Subscription plans
- Transaction: Toll payment transactions
- PaymentMethod: User's payment methods
- AccountTransaction: Account deposits and withdrawals
- TrafficData: Traffic information for toll plazas
- Notification: User notifications

## Google Maps API Integration

The application uses Google Maps API for:
1. Traffic information around toll plazas
2. Route planning with toll information
3. Finding nearby toll plazas

To use these features, you need to:
1. Obtain a Google Maps API key from the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the following APIs:
   - Maps JavaScript API
   - Directions API
   - Distance Matrix API
   - Places API
   - Geocoding API
3. Add your API key to the `.env` file

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. 