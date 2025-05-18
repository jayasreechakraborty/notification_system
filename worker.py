import sys
import os
import time
import logging
import pika
import json
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.emaill import send_email
from services.sms import send_sms
from services.in_app import save_in_app_message

def handle_message(n):
    t = n["type"]
    if t == "email":
        logger.info(f"Sending email to {n['email']}")
        send_email(n["email"], n["message"])
    elif t == "sms":
        logger.info(f"Sending SMS to {n['phone']}")
        send_sms(n["phone"], n["message"])
    elif t == "in_app":
        logger.info(f"Saving in-app message for user {n['user_id']}")
        save_in_app_message(n["user_id"], n["message"])
    else:
        logger.warning(f"Unknown notification type: {t}")

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

def connect_to_rabbitmq():
    """Connect to RabbitMQ with retry logic"""
    max_retries = 5
    retry_delay = 5  # seconds
    
    # Get RabbitMQ URL from environment variable or use localhost as fallback
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://localhost')
    logger.info(f"Connecting to RabbitMQ: {rabbitmq_url.split('@')[-1]}")  # Log only the host part for security
    
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

def main():
    while True:
        try:
            # Connect to RabbitMQ
            connection, channel = connect_to_rabbitmq()
            
            # Set up consumer
            channel.basic_consume(queue='notifications', on_message_callback=callback)
            
            logger.info("Worker started. Waiting for messages...")
            channel.start_consuming()
            
        except (AMQPConnectionError, ChannelClosedByBroker) as e:
            logger.error(f"RabbitMQ connection error: {e}")
            logger.info("Attempting to reconnect in 10 seconds...")
            time.sleep(10)
            
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            if 'connection' in locals() and connection.is_open:
                connection.close()
            break
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            logger.info("Restarting worker in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()
