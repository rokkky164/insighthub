import csv

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from io import TextIOWrapper
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["category", "business", "is_active"]
    search_fields = ["name", "sku", "description"]
    ordering_fields = ["price", "stock", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete: set is_active = False"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Reactivate a soft-deleted product"""
        product = self.get_object()
        product.is_active = True
        product.save()
        return Response({"status": "Product activated"})

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        """List products that are low on stock"""
        low_stock_products = Product.objects.filter(
            is_active=True, stock__lte=models.F("low_stock_alert")
        )
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="bulk-update-stock")
    def bulk_update_stock(self, request):
        updates = request.data
        updated = []

        for item in updates:
            try:
                product = Product.objects.get(id=item["id"])
                product.stock = item["stock"]
                product.save()
                updated.append(product.id)
            except Product.DoesNotExist:
                continue
            except KeyError:
                continue

        return Response(
            {
                "updated_ids": updated,
                "message": f"{len(updated)} products updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["put"], url_path="bulk-update")
    def bulk_update(self, request):
        updated_ids = []
        errors = []

        for data in request.data:
            try:
                product = Product.objects.get(id=data["id"])
                for field, value in data.items():
                    setattr(product, field, value)
                product.save()
                updated_ids.append(product.id)
            except Product.DoesNotExist:
                errors.append({"id": data["id"], "error": "Product not found"})
            except Exception as e:
                errors.append({"id": data.get("id"), "error": str(e)})

        return Response(
            {"updated": updated_ids, "errors": errors}, status=status.HTTP_200_OK
        )


class ProductCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "CSV file is required"}, status=400)

        decoded_file = TextIOWrapper(file.file, encoding="utf-8")
        reader = csv.DictReader(decoded_file)

        created = 0
        updated = 0
        errors = []

        for i, row in enumerate(reader, start=1):
            try:
                product_data = {
                    "name": row["name"],
                    "sku": row["sku"],
                    "price": float(row["price"]),
                    "stock": int(row["stock"]),
                    "low_stock_alert": int(row["low_stock_alert"]),
                    "category_id": int(row["category"]),
                    "business_id": int(row["business"]),
                }

                product, created_flag = Product.objects.update_or_create(
                    sku=product_data["sku"],
                    business_id=product_data["business_id"],
                    defaults=product_data,
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        return Response(
            {
                "message": "Upload complete",
                "created": created,
                "updated": updated,
                "errors": errors,
            },
            status=201,
        )


@api_view(["GET"])
def download_csv_template(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=product_template.csv"

    writer = csv.writer(response)
    writer.writerow(
        ["name", "sku", "price", "stock", "low_stock_alert", "category", "business"]
    )
    writer.writerow(["", "", 0.00, 0, 0, 1, 1])  # Example empty row

    return response


@action(detail=False, methods=["get"], url_path="export-csv")
def export_csv(self, request):
    products = self.get_queryset()

    def generate():
        yield ",".join(
            [
                "id",
                "name",
                "sku",
                "price",
                "stock",
                "low_stock_alert",
                "category",
                "business",
                "is_active",
            ]
        ) + "\n"
        for p in products:
            row = [
                str(p.id),
                p.name,
                p.sku,
                str(p.price),
                str(p.stock),
                str(p.low_stock_alert),
                str(p.category_id or ""),
                str(p.business_id),
                str(p.is_active),
            ]
            yield ",".join(row) + "\n"

    response = StreamingHttpResponse(generate(), content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=products_export.csv"
    return response
