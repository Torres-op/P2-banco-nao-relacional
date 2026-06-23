import uuid
from datetime import datetime, timezone
from app.models import StatusPedido


class PedidoRepository:
    def __init__(self, collection) -> None:
        self.collection = collection

    async def criar(self, dados: dict) -> dict:
        documento = {
            "_id": str(uuid.uuid4()),
            "nome_cliente": dados["nome_cliente"],
            "nome_produto": dados["nome_produto"],
            "quantidade": dados["quantidade"],
            "status": StatusPedido.PENDENTE.value,
            "criado_em": datetime.now(timezone.utc),
        }
        await self.collection.insert_one(documento)
        return self._serializar(documento)

    async def listar(self) -> list[dict]:
        pedidos: list[dict] = []
        async for documento in self.collection.find():
            pedidos.append(self._serializar(documento))
        return pedidos

    @staticmethod
    def _serializar(documento: dict) -> dict:
        return {
            "id": documento["_id"],
            "nome_cliente": documento["nome_cliente"],
            "nome_produto": documento["nome_produto"],
            "quantidade": documento["quantidade"],
            "status": documento["status"],
            "criado_em": documento["criado_em"],
        }
