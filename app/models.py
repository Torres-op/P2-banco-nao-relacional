from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class StatusPedido(str, Enum):
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

class PedidoCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome_cliente": "João da Silva",
                "nome_produto": "Teclado Mecânico",
                "quantidade": 2,
            }
        }
    )

    nome_cliente: str = Field(..., min_length=1, description="Nome do cliente")
    nome_produto: str = Field(..., min_length=1, description="Nome do produto")
    quantidade: int = Field(..., gt=0, description="Quantidade, deve ser maior que zero")

class PedidoResponse(BaseModel):
    id: str = Field(..., description="Identificador único do pedido")
    nome_cliente: str
    nome_produto: str
    quantidade: int
    status: StatusPedido
    criado_em: datetime
