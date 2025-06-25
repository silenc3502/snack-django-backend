from django.db import models

# 구독 상품 정의 엔티티
class Subscribe(models.Model):
    PLAN_TYPE_CHOICES =[
        ('BASIC', '베이직'),
        ('PREMIUM', '프리미엄')
    ]
    name = models.CharField(max_length=100)  # 상품명
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 가격
    duration_days = models.IntegerField(default=30)  # 구독 유효 기간 (일 수)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)  # 현재 사용 가능 여부

    class Meta:
        db_table = 'subscribe'
        app_label = 'subscribe'


