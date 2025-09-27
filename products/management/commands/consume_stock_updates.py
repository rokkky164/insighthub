from kafka import KafkaConsumer
import json
from django.core.management.base import BaseCommand
from products.models import Product


KAFKA_TOPIC = 'stock_updates'
KAFKA_SERVER = 'localhost:9092'


class Command(BaseCommand):
    help = 'Consumes stock updates from Kafka and updates Product stock'

    def handle(self, *args, **kwargs):
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_SERVER,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='stock-update-group',
        )

        self.stdout.write(self.style.SUCCESS('✅ Listening to stock updates...'))

        for message in consumer:
            data = message.value
            sku = data.get('sku')
            stock = data.get('stock')

            if not sku or stock is None:
                self.stdout.write(self.style.WARNING(f'⚠️ Invalid message: {data}'))
                continue

            try:
                product = Product.objects.get(sku=sku)
                product.stock = stock
                product.save(update_fields=['stock'])
                self.stdout.write(f"✔️ Updated {sku} to stock {stock}")
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"❌ Product with SKU '{sku}' not found."))
