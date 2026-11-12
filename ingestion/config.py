from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Service Ingestion API"
    DEBUG: bool = False

    # Redis Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # RabbitMQ Config
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    ORDER_QUEUE_NAME: str = "order_events"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
