import pika, json
import os

def publish_to_queue(data):
    # Get RabbitMQ URL from environment variable or use localhost as fallback
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://localhost')
    
    # Parse the URL to get connection parameters
    params = pika.URLParameters(rabbitmq_url)
    
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='notifications', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

