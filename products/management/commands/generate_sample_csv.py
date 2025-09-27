import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate a CSV template for bulk product upload'

    def handle(self, *args, **options):
        filename = 'product_upload_template.csv'
        filepath = os.path.join(settings.BASE_DIR, filename)

        headers = ['name', 'sku', 'price', 'stock', 'low_stock_alert', 'category', 'business']
        sample_data = [
            ['Test Product A', 'TPA001', 49.99, 100, 10, 1, 1],
            ['Test Product B', 'TPB002', 75.50, 50, 5, 2, 1]
        ]

        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(sample_data)

        self.stdout.write(self.style.SUCCESS(f'✅ CSV template generated: {filepath}'))
