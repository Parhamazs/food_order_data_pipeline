import json
import redis
import pika
from fastapi import FastAPI, HTTPException, status
from ingestion.config import settings
from ingestion.schemas import OrderCreateRequest, OrderResponse

app = FastAPI(title=settings.APP_NAME)

# connect to redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)


def send_to_rabbitmq(message: dict):
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials
        )
    )
    channel = connection.channel()
    # ساخت صف در صورتی که وجود نداشته باشد (Durable: در صورت ریستارت پاک نشود)
    channel.queue_declare(queue=settings.ORDER_QUEUE_NAME, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=settings.ORDER_QUEUE_NAME,
        body=json.dumps(message, default=str),
        properties=pika.BasicProperties(
            delivery_mode=2  # پیام پایدار ذخیره شود (Persistent)
        )
    )
    connection.close()


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_order(order: OrderCreateRequest):
    
    is_new = redis_client.set(f"idemp:{order.idempotency_key}", "PROCESSING", nx=True, ex=600)
    if not is_new:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این سفارش قبلاً دریافت شده و در حال پردازش است (Duplicate Order Detected)."
        )

    # ب) ارسال سفارش به RabbitMQ
    try:
        send_to_rabbitmq(order.model_dump())
    except Exception as exc:
        # در صورت شکست ارتباط با صف، قفل ردیس را آزاد می‌کنیم تا کاربر بتواند مجدد امتحان کند
        redis_client.delete(f"idemp:{order.idempotency_key}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"خطا در ارسال به صف پیام: {str(exc)}"
        )

    return OrderResponse(
        status="accepted",
        message="سفارش دریافت شد و برای پردازش به صف رفت.",
        idempotency_key=order.idempotency_key
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}
