import smtplib
from email.mime.text import MIMEText
from .credd import EMAIL, APP_PASSWORD  

def send_email(to, message):
    msg = MIMEText(message)
    msg["Subject"] = "Notification"
    msg["From"] = EMAIL
    msg["To"] = to

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {to}")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Please check your App Password.")
    except Exception as e:
        print("An error occurred:", e)
