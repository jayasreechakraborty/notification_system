# Notification Service 

A scalable, multi-channel notification system built with FastAPI, RabbitMQ, and SQLAlchemy. This service allows you to send notifications via email, SMS, and in-app channels through a unified API.

## Project Overview

This notification service provides a centralized system for sending various types of notifications through a single API. It uses a microservices architecture with separate components for the API and worker processes, connected through RabbitMQ for reliable message queuing.

## Architecture

The system follows a message-driven architecture with the following components:

1. **API Service (FastAPI)**:
API Documentation (when running locally): http://localhost:8000/docs

This is the Swagger UI documentation that FastAPI automatically generates
It's available once you start your application with uvicorn main:app --reload
  
   - Handles incoming HTTP requests
   - Validates notification data
   - Publishes messages to RabbitMQ queue
   - Provides endpoints for retrieving in-app notifications

2.worker Service**:
   - Consumes messages from RabbitMQ queue
   - Processes notifications based on their type
   - Sends emails, SMS, or stores in-app notifications
   - Implements retry logic for failed operations

3. **Message Queue (RabbitMQ)**:
   - Decouples the API from notification processing
   - Ensures reliable message delivery
   - Provides buffering during high load
   - Enables horizontal scaling of workers

4. **Database (SQLite/PostgreSQL)**:
   - Stores in-app notifications
   - Provides persistence for notification history
   - Supports retrieval of notifications by user ID

### System Flow

1. Client sends a notification request to the API
2. API validates the request and publishes a message to RabbitMQ
3. Worker consumes the message from the queue
4. Worker processes the notification based on its type:
   - Email: Sends via SMTP
   - SMS: Sends via Twilio
   - In-app: Stores in database
5. For in-app notifications, clients can retrieve them via the API

## Technology Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **Pydantic**: Data validation and settings management
- **RabbitMQ**: Message broker for asynchronous processing
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **Pika**: RabbitMQ client for Python
- **Twilio**: Service for sending SMS messages
- **SMTP**: Protocol for sending emails
- **SQLite**: Lightweight database for development
- **PostgreSQL**: Production-grade database for deployment
- **Uvicorn**: ASGI server for running FastAPI applications
- **Python-dotenv**: Environment variable management
- **Docker**: Containerization for consistent development and deployment
- **Render**: Cloud platform for deployment

## Project Structure

```
notification_services/
├── db/
│   ├── __init__.py
│   ├── database.py      # Database connection and session management
│   └── models.py        # SQLAlchemy models for in-app notifications
├── services/
│   ├── __init__.py
│   ├── emaill.py        # Email notification service
│   ├── sms.py           # SMS notification service using Twilio
│   ├── in_app.py        # In-app notification service with database storage
│   ├── queue_publisher.py # RabbitMQ message publishing
│   └── credd.py         # Credentials management
├── .env                 # Environment variables (not in version control)
├── .env.example         # Example environment variables
├── main.py              # FastAPI application and endpoints
├── worker.py            # Worker process for consuming messages
├── requirements.txt     # Project dependencies
├── render.yaml          # Render deployment configuration
└── README.md            # Project documentation
```

## Features

- **Multi-channel Support**: Send notifications through email, SMS, and in-app channels
- **Asynchronous Processing**: Uses RabbitMQ for reliable message queuing and processing
- **RESTful API**: Clean, well-documented API built with FastAPI
- **Persistent Storage**: Stores in-app notifications in a database (SQLite or PostgreSQL)
- **Scalable Architecture**: Separate API and worker components for horizontal scaling
- **Error Handling**: Robust error handling and retry mechanisms
- **Logging**: Comprehensive logging for debugging and monitoring
- **Health Checks**: Endpoint for monitoring service health
- **Interactive Documentation**: Auto-generated Swagger UI documentation
- **Containerization**: Docker support for consistent development and deployment

## API Endpoints

### POST /notify

This endpoint accepts notification requests and queues them for processing:

**Request Body**:
```json
{
  "type": "email",
  "message": "Your order has been shipped!",
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "status": "Notification queued."
}
```

**Validation**:
- For email notifications: `email` field is required
- For SMS notifications: `phone` and `user_id` fields are required
- For in-app notifications: `user_id` field is required

### GET /notifications/{user_id}

This endpoint retrieves in-app notifications for a specific user:

**Path Parameters**:
- `user_id`: The ID of the user whose notifications to retrieve

**Response**:
```json
{
  "user_id": "user123",
  "messages": [
    {
      "id": 1,
      "message": "Welcome to our platform!"
    },
    {
      "id": 2,
      "message": "You have a new friend request."
    }
  ]
}
```

### GET /health

This endpoint provides a simple health check for monitoring:

**Response**:
```json
{
  "status": "ok"
}
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file based on the `.env.example` template:

```
# Twilio credentials
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

# Email settings
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_FROM=notifications@example.com

# Database settings
DATABASE_URL=sqlite:///notifications.db

# RabbitMQ settings
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

## Running the Application

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional)
- RabbitMQ server (if not using Docker)
- PostgreSQL (optional, SQLite is used as fallback)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/notification_services.git
   cd notification_services
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your credentials and configuration

5. **Start RabbitMQ**:
   - If using Docker:
     ```bash
     docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
     ```
   - Or use a local installation or cloud service

6. **Run the API server**:
   ```bash
   uvicorn main:app --reload
   ```

7. **Run the worker in a separate terminal**:
   ```bash
   python worker.py
   ```

8. **Access the API**:
   - API documentation: http://localhost:8000/docs
   - Welcome page: http://localhost:8000/

### Using Docker Compose

1. **Build and start the services**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f
   ```

3. **Access the services**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

### Testing the API

You can use the Swagger UI at `/docs` to test the API or use curl/Postman:

**Send an email notification**:
```bash
curl -X POST "http://localhost:8000/notify" \
  -H "Content-Type: application/json" \
  -d '{"type": "email", "message": "Hello!", "email": "user@example.com"}'
```

**Send an SMS notification**:
```bash
curl -X POST "http://localhost:8000/notify" \
  -H "Content-Type: application/json" \
  -d '{"type": "sms", "message": "Hello!", "phone": "+1234567890", "user_id": "user123"}'
```

**Send an in-app notification**:
```bash
curl -X POST "http://localhost:8000/notify" \
  -H "Content-Type: application/json" \
  -d '{"type": "in_app", "message": "Hello!", "user_id": "user123"}'
```

**Retrieve in-app notifications**:
```bash
curl "http://localhost:8000/notifications/user123"
```

## Deployment on Render 
LINK TO THE DEPLOYED APPLICATION - https://notification-system-4m5j.onrender.com

The project includes a `render.yaml` file for easy deployment on Render.com:

1. **Create a Render account** and connect your GitHub repository

2. **Set up services**:
   - The `render.yaml` file defines two services:
     - `notification-service`: The FastAPI application
     - `notification-worker`: The background worker process

3. **Configure environment variables** in the Render dashboard:
   - Database URL (Render PostgreSQL or external)
   - RabbitMQ URL (CloudAMQP or other provider)
   - Email and SMS credentials

4. **Deploy the blueprint**:
   - Render will automatically deploy both services
   - The worker will connect to the same RabbitMQ instance as the API

5. **Access your deployed API**:
   - API will be available at `https://notification-service.onrender.com`
   - Documentation at `https://notification-service.onrender.com/docs`

## Assumptions and Design Decisions

1. **Message Format**:
   - Notifications have a type, message content, and channel-specific identifiers
   - Email notifications require an email address
   - SMS notifications require a phone number and user ID
   - In-app notifications require a user ID

2. **Error Handling**:
   - Invalid messages are rejected and not requeued
   - Messages with processing errors are requeued for retry
   - Worker implements reconnection logic for RabbitMQ
   - Database operations use session management for transaction safety

3. **Database**:
   - Only in-app notifications are stored in the database
   - Email and SMS notifications are sent directly and not stored
   - SQLite is used for development, PostgreSQL for production
   - Database URL is configurable via environment variables

4. **Security**:
   - Sensitive credentials are stored in environment variables
   - Email passwords and API keys are not hardcoded
   - The API doesn't implement authentication (would be added in production)

5. **Scalability**:
   - The worker can be scaled horizontally for higher throughput
   - RabbitMQ ensures messages are processed even if workers restart
   - Database connections use connection pooling

6. **Limitations**:
   - No rate limiting implemented
   - No user preference management
   - Basic implementation of email and SMS services
   - No authentication or authorization

## Future Enhancements

- Add authentication and authorization
- Implement rate limiting
- Add notification templates
- Support for push notifications
- User preference management
- Notification status tracking
- Analytics and reporting
- Scheduled notifications
- Docker Compose setup for local development
- Comprehensive test suite

## License

[MIT License](LICENSE)
