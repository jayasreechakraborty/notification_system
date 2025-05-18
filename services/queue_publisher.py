import pika, json

def publish_to_queue(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='notifications', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

