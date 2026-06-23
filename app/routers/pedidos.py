import logging
from fastapi import APIRouter, Depends, status
from fastapi.concurrency import run_in_threadpool
from app.brokers.kafka_service import KafkaService
from app.brokers.rabbitmq_service import RabbitMQService
from app.dependencies import (
    get_kafka_service,
    get_rabbitmq_service,
    get_repository,
)
from app.models import PedidoCreate, PedidoResponse
from app.repository import PedidoRepository


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

def _montar_evento(pedido: dict) -> dict:
    return {
        "evento": "pedido_criado",
        "id": pedido["id"],
        "nome_cliente": pedido["nome_cliente"],
        "nome_produto": pedido["nome_produto"],
        "quantidade": pedido["quantidade"],
        "status": pedido["status"],
    }

@router.post(
    "",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo pedido",
)
async def criar_pedido(
    payload: PedidoCreate,
    repo: PedidoRepository = Depends(get_repository),
    rabbitmq: RabbitMQService = Depends(get_rabbitmq_service),
    kafka: KafkaService = Depends(get_kafka_service),
) -> PedidoResponse:
    pedido = await repo.criar(payload.model_dump())
    evento = _montar_evento(pedido)

    try:
        await run_in_threadpool(rabbitmq.publish, evento)
    except Exception:
        logger.exception("Falha ao publicar a mensagem no RabbitMQ")

    try:
        await run_in_threadpool(kafka.publish, evento, pedido["id"])
    except Exception:
        logger.exception("Falha ao publicar o evento no Kafka")

    return pedido

@router.get(
    "",
    response_model=list[PedidoResponse],
    summary="Listar todos os pedidos",
)
async def listar_pedidos(
    repo: PedidoRepository = Depends(get_repository),
) -> list[PedidoResponse]:
    return await repo.listar()
