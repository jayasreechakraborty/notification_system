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

## Integration Details

### FastAPI Implementation

The FastAPI application is implemented in `main.py` with the following key components:

1. **API Initialization**:
   ```python
   app = FastAPI(
       title="Notification Service API",
       description="API for sending email, SMS, and in-app notifications",
       version="1.0.0"
   )
   ```

2. **Data Models with Pydantic**:
   ```python
   class Notification(BaseModel):
       type: str  # "email", "sms", or "in_app"
       message: str
       email: EmailStr = None
       phone: str = None
       user_id: str = None
   ```

3. **POST Endpoint for Sending Notifications**:
   ```python
   @app.post("/notify")
   def send(notification: Notification):
       # Validation logic
       if notification.type == "email" and not notification.email:
           return {"error": "Please provide an email address."}
       if notification.type == "sms" and (not notification.phone or not notification.user_id):
           return {"error": "Phone and user ID are needed for SMS."}
       if notification.type == "in_app" and not notification.user_id:
           return {"error": "User ID is required for in-app notifications."}

       # Queue the notification
       publish_to_queue(notification.model_dump())
       return {"status": "Notification queued."}
   ```

4. **GET Endpoint for Retrieving In-App Notifications**:
   ```python
   @app.get("/notifications/{user_id}")
   def get_notifications(user_id: str):
       messages = get_user_messages(user_id)
       return {"user_id": user_id, "messages": messages}
   ```

5. **Health Check Endpoint**:
   ```python
   @app.get("/health")
   def health_check():
       return {"status": "ok"}
   ```

### RabbitMQ Integration

The integration with RabbitMQ is handled through two main components:

1. **Publisher (in services/queue_publisher.py)**:
   ```python
   def publish_to_queue(data):
       # Get RabbitMQ URL from environment variable or use localhost as fallback
       rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://localhost')
       
       # Parse the URL to get connection parameters
       params = pika.URLParameters(rabbitmq_url)
       
       # Connect to RabbitMQ
       connection = pika.BlockingConnection(params)
       channel = connection.channel()

       # Declare a durable queue to ensure messages persist even if RabbitMQ restarts
       channel.queue_declare(queue='notifications', durable=True)
       
       # Publish the message with delivery_mode=2 for persistence
       channel.basic_publish(
           exchange='',
           routing_key='notifications',
           body=json.dumps(data),
           properties=pika.BasicProperties(delivery_mode=2)
       )
       connection.close()
   ```

2. **Consumer (in worker.py)**:
   ```python
   def callback(ch, method, _, body):
       try:
           message = json.loads(body)
           logger.info(f"Processing message: {message['type']}")
           handle_message(message)
           ch.basic_ack(delivery_tag=method.delivery_tag)
           logger.info(f"Successfully processed message")
       except json.JSONDecodeError:
           logger.error(f"Invalid JSON in message: {body}")
           ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
       except KeyError as e:
           logger.error(f"Missing key in message: {e}")
           ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
       except Exception as e:
           logger.error(f"Error processing message: {e}", exc_info=True)
           # Requeue the message for later processing
           ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
   ```

3. **Connection Management with Retry Logic**:
   ```python
   def connect_to_rabbitmq():
       """Connect to RabbitMQ with retry logic"""
       max_retries = 5
       retry_delay = 5  # seconds
       
       # Get RabbitMQ URL from environment variable or use localhost as fallback
       rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://localhost')
       logger.info(f"Connecting to RabbitMQ: {rabbitmq_url.split('@')[-1]}")
       
       for attempt in range(max_retries):
           try:
               # Parse the URL to get connection parameters
               params = pika.URLParameters(rabbitmq_url)
               params.heartbeat = 600  # Set a longer heartbeat interval
               
               # Connect to RabbitMQ
               connection = pika.BlockingConnection(params)
               channel = connection.channel()
               
               # Declare the queue
               channel.queue_declare(queue='notifications', durable=True)
               
               # Set QoS
               channel.basic_qos(prefetch_count=1)
               
               logger.info("Successfully connected to RabbitMQ")
               return connection, channel
               
           except AMQPConnectionError as e:
               if attempt < max_retries - 1:
                   logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt+1}/{max_retries}): {e}")
                   time.sleep(retry_delay)
               else:
                   logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts: {e}")
                   raise
   ```

### Docker Integration

The project uses Docker for containerization, making it easy to run the application consistently across different environments:

1. **Dockerfile for the API Service**:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Dockerfile for the Worker Service**:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "worker.py"]
   ```

3. **Docker Compose Configuration**:
   ```yaml
   version: '3'

   services:
     rabbitmq:
       image: rabbitmq:3-management
       ports:
         - "5672:5672"
         - "15672:15672"
       volumes:
         - rabbitmq_data:/var/lib/rabbitmq
       environment:
         - RABBITMQ_DEFAULT_USER=guest
         - RABBITMQ_DEFAULT_PASS=guest

     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
         - DATABASE_URL=sqlite:///./notifications.db
       depends_on:
         - rabbitmq
       command: uvicorn main:app --host 0.0.0.0 --port 8000

     worker:
       build: .
       environment:
         - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
         - DATABASE_URL=sqlite:///./notifications.db
       depends_on:
         - rabbitmq
       command: python worker.py

   volumes:
     rabbitmq_data:
   ```

### Database Integration

The database integration is handled through SQLAlchemy:

1. **Database Connection Setup (in db/database.py)**:
   ```python
   # Get database URL from environment variable or use SQLite as fallback
   DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notifications.db")
   
   # Handle special case for PostgreSQL URLs from Render
   if DATABASE_URL.startswith("postgres://"):
       DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
   
   # Create SQLAlchemy engine with appropriate connect_args
   connect_args = {}
   if DATABASE_URL.startswith("sqlite"):
       connect_args = {"check_same_thread": False}
       
   engine = create_engine(
       DATABASE_URL, 
       connect_args=connect_args,
       pool_pre_ping=True  # This helps with connection issues
   )
   
   # Create session factory
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   ```

2. **Database Models (in db/models.py)**:
   ```python
   class InAppMessage(Base):
       __tablename__ = "in_app_messages"
       
       id = Column(Integer, primary_key=True, index=True)
       user_id = Column(String(50), index=True)
       message = Column(Text)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

3. **Database Operations (in services/in_app.py)**:
   ```python
   def save_in_app_message(user_id: str, message: str):
       try:
           with SessionLocal() as db:
               msg = InAppMessage(user_id=user_id, message=message)
               db.add(msg)
               db.commit()
               db.refresh(msg)
               return {"id": msg.id, "user_id": msg.user_id, "message": msg.message}
       except SQLAlchemyError:
           return None

   def get_user_messages(user_id: str):
       try:
           with SessionLocal() as db:
               return [{"id": m.id, "message": m.message} for m in db.query(InAppMessage).filter_by(user_id=user_id)]
       except SQLAlchemyError:
           return []
   ```

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
