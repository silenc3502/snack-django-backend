from django.db import models

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', '결제 대기'
    COMPLETED = 'COMPLETED', '주문 완료'
