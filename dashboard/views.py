import csv

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.utils.timezone import now
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django.db.models import Sum, F

from sales.models import Sale, SaleItem, Purchase
from billing.models import Invoice, BillingPayment
from products.models import Product


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now().date()
        start_of_month = today.replace(day=1)

        # Total sales today and this month
        total_sales_today = (
            Sale.objects.filter(sale_date__date=today).aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )
        total_sales_month = (
            Sale.objects.filter(sale_date__date__gte=start_of_month).aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # Top-selling products
        top_products = (
            SaleItem.objects.values("product__name")
            .annotate(quantity_sold=Sum("quantity"))
            .order_by("-quantity_sold")[:5]
        )

        # Low stock products
        low_stock = Product.objects.filter(inventory_quantity__lt=5).values(
            "name", "inventory_quantity"
        )

        return Response(
            {
                "total_sales_today": total_sales_today,
                "total_sales_month": total_sales_month,
                "top_products": list(top_products),
                "low_stock": list(low_stock),
            }
        )


class SalesCSVExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = parse_date(request.GET.get("start"))
        end = parse_date(request.GET.get("end"))

        if not start or not end:
            return Response({"error": "start and end date required"}, status=400)

        sales = Sale.objects.filter(
            sale_date__date__gte=start, sale_date__date__lte=end
        ).prefetch_related("items", "customer")

        # Generate CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="sales_{start}_{end}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            ["Sale ID", "Date", "Customer", "Product", "Quantity", "Price", "Subtotal"]
        )

        for sale in sales:
            for item in sale.items.all():
                writer.writerow(
                    [
                        sale.id,
                        sale.sale_date.strftime("%Y-%m-%d %H:%M"),
                        sale.customer.name if sale.customer else "Guest",
                        item.product.name if item.product else "N/A",
                        item.quantity,
                        item.price,
                        item.subtotal,
                    ]
                )

        return response


class SalesChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = parse_date(request.GET.get("start"))
        end = parse_date(request.GET.get("end"))

        if not start or not end:
            return Response({"error": "start and end date required"}, status=400)

        sales_by_day = (
            Sale.objects.filter(sale_date__date__gte=start, sale_date__date__lte=end)
            .annotate(day=TruncDay("sale_date"))
            .values("day")
            .annotate(total=Sum("total_amount"))
            .order_by("day")
        )

        # Return chart-friendly format
        labels = [entry["day"].strftime("%Y-%m-%d") for entry in sales_by_day]
        totals = [entry["total"] for entry in sales_by_day]

        return Response({"labels": labels, "totals": totals})


class ProductSalesChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = parse_date(request.GET.get("start"))
        end = parse_date(request.GET.get("end"))
        if not start or not end:
            return Response({"error": "start and end date required"}, status=400)

        # Aggregate sale items by day and product
        sales_data = (
            SaleItem.objects.filter(
                sale__sale_date__date__gte=start, sale__sale_date__date__lte=end
            )
            .annotate(day=TruncDay("sale__sale_date"))
            .values("day", "product__name")
            .annotate(total=Sum("subtotal"))
            .order_by("day")
        )

        # Prepare data structure for frontend charts
        # {
        #   "labels": [dates],
        #   "datasets": {
        #       "Product A": [values per day],
        #       "Product B": [values per day],
        #       ...
        #   }
        # }

        # Extract sorted unique dates and products
        dates = sorted({entry["day"].date() for entry in sales_data})
        products = sorted({entry["product__name"] for entry in sales_data})

        # Initialize dataset dict: {product: [0]*len(dates)}
        data_map = {product: [0] * len(dates) for product in products}

        # Map date to index
        date_index = {date: idx for idx, date in enumerate(dates)}

        # Fill data_map
        for entry in sales_data:
            d = entry["day"].date()
            p = entry["product__name"]
            idx = date_index[d]
            data_map[p][idx] = float(
                entry["total"]
            )  # convert Decimal to float for JSON

        # Format labels as strings
        labels = [date.strftime("%Y-%m-%d") for date in dates]

        return Response({"labels": labels, "datasets": data_map})


class CustomerSalesChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = parse_date(request.GET.get("start"))
        end = parse_date(request.GET.get("end"))
        if not start or not end:
            return Response({"error": "start and end date required"}, status=400)

        # Aggregate sales by day and customer
        sales_data = (
            Sale.objects.filter(sale_date__date__gte=start, sale_date__date__lte=end)
            .annotate(day=TruncDay("sale_date"))
            .values("day", "customer__name")
            .annotate(total=Sum("total_amount"))
            .order_by("day")
        )

        # Extract unique dates and customers
        dates = sorted({entry["day"].date() for entry in sales_data})
        customers = sorted({entry["customer__name"] or "Guest" for entry in sales_data})

        data_map = {customer: [0] * len(dates) for customer in customers}
        date_index = {date: idx for idx, date in enumerate(dates)}

        for entry in sales_data:
            d = entry["day"].date()
            customer = entry["customer__name"] or "Guest"
            idx = date_index[d]
            data_map[customer][idx] = float(entry["total"])

        labels = [date.strftime("%Y-%m-%d") for date in dates]

        return Response({"labels": labels, "datasets": data_map})


class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business = request.user.business  # assuming each user is linked to a business

        # ----- Sales Metrics -----
        sales = Sale.objects.filter(customer__business=business)
        total_sales = sales.aggregate(total=Sum("total_amount"))["total"] or 0
        total_sale_invoices = Invoice.objects.filter(
            sale__customer__business=business
        ).count()
        avg_invoice_value = (
            total_sales / total_sale_invoices if total_sale_invoices else 0
        )

        # Top Selling Products
        top_products = (
            SaleItem.objects.filter(sale__customer__business=business)
            .values("product__name")
            .annotate(
                total_qty=Sum("quantity"), total_sales=Sum(F("quantity") * F("price"))
            )
            .order_by("-total_qty")[:5]
        )

        # ----- Purchase Metrics -----
        purchases = Purchase.objects.filter(business=business)
        total_purchases = purchases.aggregate(total=Sum("total_amount"))["total"] or 0
        total_purchase_invoices = Invoice.objects.filter(
            purchase__business=business
        ).count()
        avg_purchase_value = (
            total_purchases / total_purchase_invoices if total_purchase_invoices else 0
        )

        # ----- Invoices & Payments -----
        pending_invoices = Invoice.objects.filter(
            business=business, status="pending"
        ).count()
        paid_invoices = Invoice.objects.filter(business=business, status="paid").count()
        overdue_invoices = Invoice.objects.filter(
            business=business, status="overdue"
        ).count()

        # ----- Stock Levels -----
        low_stock_products = Product.objects.filter(
            business=business, stock__lte=F("low_stock_alert")
        ).values("name", "stock", "low_stock_alert")

        # ----- Cash & Receivables -----
        total_payments_received = (
            Payment.objects.filter(
                invoice__sale__customer__business=business, is_confirmed=True
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        total_receivables = (
            Invoice.objects.filter(business=business, status="pending").aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        # ----- Response -----
        data = {
            "sales": {
                "total_sales": total_sales,
                "total_invoices": total_sale_invoices,
                "avg_invoice_value": avg_invoice_value,
                "top_products": list(top_products),
            },
            "purchases": {
                "total_purchases": total_purchases,
                "total_invoices": total_purchase_invoices,
                "avg_purchase_value": avg_purchase_value,
            },
            "invoices": {
                "pending": pending_invoices,
                "paid": paid_invoices,
                "overdue": overdue_invoices,
            },
            "stock": list(low_stock_products),
            "cash": {
                "total_received": total_payments_received,
                "total_receivables": total_receivables,
            },
        }

        return Response(data)
