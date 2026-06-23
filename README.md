# API de Gerenciamento de Pedidos

API REST para **cadastro e consulta de pedidos**, construída com **FastAPI**.
Os pedidos são persistidos no **MongoDB** (banco NoSQL) e, a cada criação, a
aplicação publica:

- uma **mensagem no RabbitMQ** (fila), e
- um **evento no Kafka** (tópico),

para que outros sistemas possam reagir à criação do pedido.

Projeto desenvolvido como atividade da disciplina de Backend (Engenharia de
Software).

---

## Sumário

- [Arquitetura](#arquitetura)
- [Modelo de dados](#modelo-de-dados)
- [Endpoints](#endpoints)
- [Como executar (Docker Compose)](#como-executar-docker-compose)
- [Como testar a API manualmente](#como-testar-a-api-manualmente)
- [Verificando a mensageria](#verificando-a-mensageria)
- [Testes automatizados](#testes-automatizados)
- [Executando localmente sem Docker](#executando-localmente-sem-docker)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Decisões de projeto](#decisões-de-projeto)

---

## Arquitetura

```
                         ┌──────────────────────┐
       POST /pedidos     │                      │   insert_one()
  ────────────────────►  │      FastAPI         │ ───────────────►  MongoDB
       GET  /pedidos     │  (app de pedidos)    │   find()          (coleção
  ◄────────────────────  │                      │ ◄───────────────   "pedidos")
                         └─────────┬───────┬────┘
                                   │       │
                       publica     │       │   publica
                     mensagem      │       │   evento
                                   ▼       ▼
                            RabbitMQ      Kafka  ◄── Zookeeper
                          (fila            (tópico
                       "pedidos.criados") "pedidos.criados")
```

Ao criar um pedido a aplicação executa, nesta ordem:

1. gera um **identificador único** (UUID);
2. **persiste** o pedido no MongoDB com status inicial `PENDENTE`;
3. **publica** uma mensagem no RabbitMQ;
4. **publica** um evento no Kafka.

## Modelo de dados

Cada pedido possui:

| Campo          | Tipo     | Descrição                                  |
| -------------- | -------- | ------------------------------------------ |
| `id`           | string   | Identificador único (UUID) gerado pela API |
| `nome_cliente` | string   | Nome do cliente                            |
| `nome_produto` | string   | Nome do produto                            |
| `quantidade`   | inteiro  | Quantidade (maior que zero)                |
| `status`       | string   | Status do pedido (inicial: `PENDENTE`)     |
| `criado_em`    | datetime | Data/hora de criação (UTC)                 |

## Endpoints

| Método | Rota        | Descrição                          | Sucesso |
| ------ | ----------- | ---------------------------------- | ------- |
| `POST` | `/pedidos`  | Cadastra um novo pedido            | `201`   |
| `GET`  | `/pedidos`  | Lista todos os pedidos cadastrados | `200`   |
| `GET`  | `/health`   | Verificação de saúde da API        | `200`   |

Documentação interativa (Swagger UI) disponível em **http://localhost:8000/docs**.

---

## Como executar (Docker Compose)

**Pré-requisito:** Docker + Docker Compose instalados.

Um único comando sobe **todos** os serviços (FastAPI, MongoDB, RabbitMQ,
Kafka e Zookeeper):

```bash
docker compose up --build
```

Aguarde os serviços ficarem saudáveis (a API só inicia depois que MongoDB,
RabbitMQ e Kafka estão prontos). Depois acesse:

- API / Swagger: http://localhost:8000/docs
- Painel do RabbitMQ: http://localhost:15672  (usuário: `guest` / senha: `guest`)

Para parar e remover os containers:

```bash
docker compose down
```

Para remover também os dados do MongoDB (volume):

```bash
docker compose down -v
```

## Como testar a API manualmente

Cadastrar um pedido:

```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"nome_cliente": "João da Silva", "nome_produto": "Teclado Mecânico", "quantidade": 2}'
```

Resposta (exemplo):

```json
{
  "id": "f0c3b6c0-9b2e-4f2a-9d1a-6f1e2c3b4a5d",
  "nome_cliente": "João da Silva",
  "nome_produto": "Teclado Mecânico",
  "quantidade": 2,
  "status": "PENDENTE",
  "criado_em": "2026-06-23T12:00:00Z"
}
```

Listar os pedidos:

```bash
curl http://localhost:8000/pedidos
```

> No Windows (PowerShell) você pode usar `Invoke-RestMethod` ou simplesmente
> testar pelo Swagger UI em `/docs`.

## Verificando a mensageria

Existem dois scripts de exemplo para **consumir** o que a API publica.

**RabbitMQ** — também é possível ver a fila `pedidos.criados` no painel
http://localhost:15672. Para consumir via script:

```bash
pip install pika
python scripts/consumir_rabbitmq.py
```

**Kafka** — consumir o tópico `pedidos.criados`:

```bash
pip install confluent-kafka
python scripts/consumir_kafka.py
```

Com um consumidor rodando, crie um pedido (POST `/pedidos`) e observe a
mensagem/evento aparecer no terminal.

---

## Testes automatizados

Os testes usam **Pytest** e validam, no mínimo, o **cadastro** e a
**listagem** de pedidos. Eles rodam **sem precisar de infraestrutura no ar**:
o MongoDB é simulado em memória (`mongomock-motor`) e os publicadores de
RabbitMQ/Kafka são substituídos por dublês.

```bash
# 1. crie e ative um ambiente virtual (opcional, recomendado)
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 2. instale as dependências de desenvolvimento/teste
pip install -r requirements-dev.txt

# 3. rode os testes
pytest
```

Casos cobertos:

- cadastro retorna `201` com os dados corretos;
- cada pedido recebe um **id único**;
- status inicial é sempre **`PENDENTE`**;
- a criação **publica** no RabbitMQ e no Kafka;
- payloads inválidos retornam `422`;
- listagem vazia retorna `[]`;
- listagem retorna todos os pedidos cadastrados.

## Executando localmente sem Docker

Caso queira rodar apenas a API localmente (precisa de MongoDB, RabbitMQ e
Kafka acessíveis):

```bash
pip install -r requirements.txt
cp .env.example .env          # ajuste os hosts/portas se necessário
uvicorn app.main:app --reload
```

## Estrutura do projeto

```
.
├── app/
│   ├── main.py                 # cria a aplicação FastAPI e o ciclo de vida
│   ├── config.py               # configurações via variáveis de ambiente
│   ├── models.py               # modelos Pydantic (entrada/saída) e StatusPedido
│   ├── database.py             # conexão com o MongoDB (Motor)
│   ├── repository.py           # acesso a dados dos pedidos (padrão Repository)
│   ├── dependencies.py         # injeção de dependências (facilita os testes)
│   ├── routers/
│   │   └── pedidos.py          # endpoints POST /pedidos e GET /pedidos
│   └── brokers/
│       ├── rabbitmq_service.py # RabbitMQService (publica na fila)
│       └── kafka_service.py    # KafkaService (publica no tópico)
├── tests/
│   ├── conftest.py             # fixtures e dublês (Mongo/RabbitMQ/Kafka)
│   └── test_pedidos.py         # testes de cadastro e listagem
├── scripts/
│   ├── consumir_rabbitmq.py    # consumidor de exemplo (verificação manual)
│   └── consumir_kafka.py       # consumidor de exemplo (verificação manual)
├── Dockerfile                  # imagem da API
├── docker-compose.yml          # API + MongoDB + RabbitMQ + Kafka + Zookeeper
├── requirements.txt            # dependências de runtime
├── requirements-dev.txt        # dependências para testes
├── pytest.ini                  # configuração do Pytest
└── .env.example                # exemplo de variáveis de ambiente
```

## Decisões de projeto

- **Banco NoSQL (MongoDB):** os pedidos ficam em uma coleção dedicada
  (`pedidos`). O `_id` do documento é o próprio UUID gerado pela aplicação.
- **Mensageria "best-effort":** a persistência é o passo crítico. Se o
  RabbitMQ ou o Kafka estiverem indisponíveis no momento da criação, o erro
  é registrado em log, mas a requisição **não falha** — o pedido já foi
  salvo. Isso evita que uma instabilidade na mensageria derrube o cadastro.
- **Publicação fora do event loop:** as publicações (que são síncronas) rodam
  em uma thread separada (`run_in_threadpool`) para não bloquear o servidor
  assíncrono.
- **Injeção de dependências:** banco e publicadores são fornecidos via
  `Depends`, o que permite substituí-los facilmente nos testes.
- **Imports preguiçosos de `pika`/`confluent-kafka`:** assim os testes rodam
  sem essas bibliotecas instaladas e sem a infraestrutura no ar.
