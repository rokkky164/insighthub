import csv
from kafka import KafkaProducer
import json
from django.core.management.base import BaseCommand
from django.conf import settings
import os


KAFKA_TOPIC = "stock_updates"
KAFKA_SERVER = "localhost:9092"


class Command(BaseCommand):
    help = "Reads CSV and publishes stock updates to Kafka"

    def handle(self, *args, **kwargs):
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        csv_path = os.path.join(settings.BASE_DIR, "stock_import.csv")
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR("CSV file not found."))
            return

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                data = {
                    "sku": row["sku"],
                    "stock": int(row["stock"]),
                }
                producer.send(KAFKA_TOPIC, value=data)
                count += 1

        producer.flush()
        self.stdout.write(
            self.style.SUCCESS(f"✅ Published {count} stock updates to Kafka.")
        )
