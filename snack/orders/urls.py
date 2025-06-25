from django.urls import path
from rest_framework.routers import DefaultRouter
from orders.controller.orders_controller import OrderController

router = DefaultRouter()
router.register(r"orders", OrderController, basename='orders')

urlpatterns = [
    path('create', OrderController.as_view({'post': 'requestCreateOrder'}), name='request-create-order'),
]

# DRF router의 URL을 포함
urlpatterns += router.urls
