from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    ProductCategoryViewSet,
    ProductCSVUploadView,
    download_csv_template,
    export_csv
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"products-categories", ProductCategoryViewSet, basename="category")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/products/upload-csv/",
        ProductCSVUploadView.as_view(),
        name="upload-products-csv",
    ),
    path(
        "api/products/csv-template/",
        download_csv_template,
        name="download-products-csv-template",
    ),
    path("api/products/export-csv/", export_csv, name="export_csv")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
