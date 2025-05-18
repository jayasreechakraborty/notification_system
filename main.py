import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from services.queue_publisher import publish_to_queue
from services.in_app import get_user_messages
# Import database components
from db.database import engine
from db.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

class Notification(BaseModel):
    type: str  # "email", "sms", or "in_app"
    message: str
    email: EmailStr = None
    phone: str = None
    user_id: str = None

@app.post("/notify")
def send(notification: Notification):
    if notification.type == "email" and not notification.email:
        return {"error": "Please provide an email address."}
    if notification.type == "sms" and (not notification.phone or not notification.user_id):
        return {"error": "Phone and user ID are needed for SMS."}
    if notification.type == "in_app" and not notification.user_id:
        return {"error": "User ID is required for in-app notifications."}

    # Queue the notification
    publish_to_queue(notification.model_dump())
    return {"status": "Notification queued."}

@app.get("/notifications/{user_id}")
def get_notifications(user_id: str):
    messages = get_user_messages(user_id)
    return {"user_id": user_id, "messages": messages}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# To run the FastAPI app, use the command:      
# uvicorn main:app --reload
# This will start the server at http://localhost:8000
# You can test the API using tools like Postman or curl.
# Example curl command to send a notification:
# curl -X POST "http://localhost:8000/notify" -H "Content-Type: application/json" -d '{"type": "email", "message": "Hello!", "email": "user@example.com"}'

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

