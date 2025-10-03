from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Sale
from .serializers import SaleSerializer
from .filters import SaleFilter
from .permissions import IsStaffUser


class SaleViewSet(viewsets.ModelViewSet):
    queryset = (
        Sale.objects.all()
        .select_related("customer", "business")
        .prefetch_related("items__product")
    )
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    filterset_class = SaleFilter

    @action(detail=True, methods=["post"])
    def return_item(self, request, pk=None):
        sale = self.get_object()
        sale_item_id = request.data.get("sale_item_id")
        quantity = int(request.data.get("quantity", 0))

        try:
            item = sale.items.get(id=sale_item_id)
        except SaleItem.DoesNotExist:
            return Response({"error": "Sale item not found."}, status=404)

        if quantity > item.quantity:
            return Response({"error": "Cannot return more than sold."}, status=400)

        # Restore inventory
        item.product.inventory_quantity += quantity
        item.product.save()

        # Optionally adjust subtotal
        item.quantity -= quantity
        item.subtotal = item.price * item.quantity
        item.save()

        # Update sale total
        sale.total_amount = sum(i.subtotal for i in sale.items.all())
        sale.save()

        return Response({"status": "item returned"})

    @action(detail=True, methods=["get"])
    def invoice(self, request, pk=None):
        sale = self.get_object()
        html_string = render_to_string("sales/invoice.html", {"sale": sale})
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="invoice_{sale.id}.pdf"'
        return response
