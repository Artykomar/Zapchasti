from django.urls import path

from . import views

app_name = "warehouse"
urlpatterns = [
    path("", views.overview, name="overview"),
    path("parts/", views.parts, name="parts"),
    path("parts/new/", views.part_detail, name="part-new"),
    path("parts/<int:pk>/", views.part_detail, name="part"),
    path("parts/<int:pk>/adjust/", views.part_adjust, name="part-adjust"),
    path("purchases/", views.purchases, name="purchases"),
    path("purchases/new/", views.purchase_create, name="purchase-new"),
    path("purchases/<int:pk>/", views.purchase_detail, name="purchase"),
    path("purchases/<int:pk>/action/", views.purchase_action, name="purchase-action"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:pk>/", views.order_detail, name="order"),
    path("orders/<int:pk>/action/", views.order_action, name="order-action"),
    path("shipments/", views.shipments, name="shipments"),
    path("shipments/order/<int:order_id>/", views.shipment_detail, name="shipment"),
    path("shipments/<int:pk>/action/", views.shipment_action, name="shipment-action"),
    path("shipments/<int:pk>/label/", views.shipment_label, name="shipment-label"),
    path("activity/", views.activity, name="activity"),
]
