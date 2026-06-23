import json
import os

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE = os.getenv("RABBITMQ_QUEUE", "pedidos.criados")


def callback(ch, method, properties, body):
    mensagem = json.loads(body)
    print(f"[RabbitMQ] Pedido recebido: {mensagem}")


def main() -> None:
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.basic_consume(queue=QUEUE, on_message_callback=callback, auto_ack=True)
    print(f"Aguardando mensagens na fila '{QUEUE}'. CTRL+C para sair.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    main()
