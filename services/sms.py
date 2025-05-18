from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

# Get Twilio credentials from environment variables
SID = os.getenv("TWILIO_ACCOUNT_SID")
TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM = os.getenv("TWILIO_PHONE_NUMBER")

if not SID or not TOKEN or not FROM:
    raise EnvironmentError("Missing one or more required Twilio environment variables.")

client = Client(SID, TOKEN)

def send_sms(to, message):
    try:
        client.messages.create(
            body=message,
            from_=FROM,
            to=to
        )
        print(f"SMS sent to {to}")
    except Exception as e:
        print(f"SMS failed:", e)
