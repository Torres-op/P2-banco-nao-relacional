from app.brokers.kafka_service import KafkaService
from app.brokers.rabbitmq_service import RabbitMQService
from app.database import get_collection
from app.repository import PedidoRepository


_rabbitmq_service = RabbitMQService()
_kafka_service = KafkaService()

def get_repository() -> PedidoRepository:
    return PedidoRepository(get_collection())

def get_rabbitmq_service() -> RabbitMQService:
    return _rabbitmq_service

def get_kafka_service() -> KafkaService:
    return _kafka_service
