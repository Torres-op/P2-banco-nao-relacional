import json
import logging
from app.config import settings


logger = logging.getLogger(__name__)

class RabbitMQService:
    def __init__(self, url: str | None = None, queue: str | None = None) -> None:
        self.url = url or settings.rabbitmq_url
        self.queue = queue or settings.rabbitmq_queue

    def publish(self, mensagem: dict) -> None:
        import pika

        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self.queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=self.queue,
                body=json.dumps(mensagem, default=str).encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )
            logger.info("Mensagem publicada no RabbitMQ (fila '%s')", self.queue)
        finally:
            connection.close()
