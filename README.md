# Music Booking Platform API

## Overview

This API powers a music booking platform that connects artists with venues and event organizers. It handles artist profiles, venue management, event creation, bookings, and payment processing through Monnify.

## Key Features

- **User Authentication**: JWT-based authentication system
- **Artist Profiles**: Manage artist information and availability
- **Venue Management**: Create and manage performance venues
- **Event Booking**: Book artists for specific events
- **Payment Processing**: Integrated Monnify payment gateway
- **Reviews & Ratings**: Rate and review artists after events

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Artists
- `GET /api/artists/` - List all artists
- `POST /api/artists/` - Create artist profile
- `GET /api/artists/<id>/` - Get artist details
- `PUT /api/artists/<id>/` - Update artist profile

### Venues
- `GET /api/venues/` - List all venues
- `POST /api/venues/` - Create new venue
- `GET /api/venues/<id>/` - Get venue details

### Events
- `GET /api/events/` - List upcoming events
- `POST /api/events/` - Create new event
- `GET /api/events/<id>/` - Get event details

### Bookings
- `GET /api/bookings/` - List user's bookings
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/<uuid>/` - Get booking details

### Payments
- `POST /api/payments/` - Initialize payment
- `GET /api/payments/verify/<transaction_ref>/` - Verify payment status

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Monnify API credentials

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your.git](https://github.com/Taofeeq97/MUSICAPPTEST.git
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Start development server:
   ```bash
   python manage.py runserver
   ```

## Payment Flow

1. Client creates booking
2. System initializes Monnify payment
3. User redirected to Monnify checkout
4. Monnify processes payment
6. System verifies and confirms payment



Configure these environment variables in production:
- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `MONNIFY_API_KEY`
- `MONNIFY_SECRET_KEY`
- `MONNIFY_CONTRACT_CODE`
- `SECRET_KEY`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`

## License

This project is licensed under the MIT License.
