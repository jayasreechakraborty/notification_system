import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import pika, json
from services.emaill import send_email
from services.sms import send_sms
from services.in_app import save_in_app_message

def handle_message(n):
    t = n["type"]
    if t == "email":
        send_email(n["email"], n["message"])
    elif t == "sms":
        send_sms(n["phone"], n["message"])
    elif t == "in_app":
        save_in_app_message(n["user_id"], n["message"])

def callback(ch, method, _, body):
    try:
        handle_message(json.loads(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Processed:", body)
    except Exception as e:
        print("Error:", e)

def main():
    c = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    ch = c.channel()
    ch.queue_declare(queue='notifications', durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue='notifications', on_message_callback=callback)
    print("Waiting for messages...")
    ch.start_consuming()

if __name__ == "__main__":
    main()
