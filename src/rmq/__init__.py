

from src.rmq.publisher import RabbitMQPublisher

rmq_publisher = RabbitMQPublisher("amqp://guest:guest@localhost/", "user_registration_queue")

def get_rmq_publisher():
    return rmq_publisher