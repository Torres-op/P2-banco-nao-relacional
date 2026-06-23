import json
import logging
from app.config import settings


logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self, bootstrap_servers: str | None = None, topic: str | None = None) -> None:
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.topic = topic or settings.kafka_topic
        self._producer = None

    def _obter_producer(self):
        if self._producer is None:
            from confluent_kafka import Producer

            self._producer = Producer({"bootstrap.servers": self.bootstrap_servers})
        return self._producer

    def publish(self, evento: dict, chave: str | None = None) -> None:
        producer = self._obter_producer()
        producer.produce(
            self.topic,
            key=chave.encode("utf-8") if chave else None,
            value=json.dumps(evento, default=str).encode("utf-8"),
        )
        producer.flush(5)
        logger.info("Evento publicado no Kafka (tópico '%s')", self.topic)
