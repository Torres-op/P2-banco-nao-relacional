from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "API para Gerenciamento de Produtos"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "pedidos_db"
    mongo_collection: str = "pedidos"

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_queue: str = "pedidos.criados"

    kafka_bootstrap_servers: str = "localhost:29092"
    kafka_topic: str = "pedidos.criados"


settings = Settings()
