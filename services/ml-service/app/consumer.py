import os, json, re, asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .model import predict_category

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC_IN = os.getenv("TOPIC_EXPENSES_RAW", "expenses.raw")
TOPIC_OUT = os.getenv("TOPIC_EXPENSES_PARSED", "expenses.parsed")

MERCHANT_PAT = re.compile(r"(at|from)\s+([A-Za-z0-9'\-& ]{2,})", re.IGNORECASE)

async def run_consumer():
    consumer = AIOKafkaConsumer(
        TOPIC_IN, bootstrap_servers=BOOTSTRAP, group_id="ml-parser", enable_auto_commit=True
    )
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP)
    await consumer.start()
    await producer.start()
    try:
        async for msg in consumer:
            try:
                evt = json.loads(msg.value.decode("utf-8"))
                desc = evt.get("description", "")
                m = MERCHANT_PAT.search(desc)
                merchant = m.group(2).strip() if m else None
                category = predict_category(desc if desc else "")
                evt["merchant"] = merchant
                evt["category"] = category
                await producer.send_and_wait(TOPIC_OUT, json.dumps(evt).encode("utf-8"))
            except Exception as e:
                # swallow & continue
                pass
    finally:
        await consumer.stop()
        await producer.stop()
