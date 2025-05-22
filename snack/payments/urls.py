from django.urls import path
from rest_framework.routers import DefaultRouter
from payments.controller.payments_controller import PaymentsController

router = DefaultRouter()
router.register(r"payments", PaymentsController, basename='payments')

urlpatterns = [
    path('process', PaymentsController.as_view({ 'post': 'requestProcessPayments' }), name='request-process-payments'),
]

# DRF router의 URL을 포함
urlpatterns += router.urls
