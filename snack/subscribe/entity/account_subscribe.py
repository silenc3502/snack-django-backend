from django.db import models
from account.entity.account import Account
from subscribe.entity.subscribe import Subscribe

class AccountSubscribe(models.Model):
    subscriber = models.ForeignKey(Account, on_delete=models.CASCADE)  # 구독 소유 유저
    plan = models.ForeignKey(Subscribe, on_delete=models.PROTECT)  # 연결된 구독 상품
    start_date = models.DateTimeField(auto_now_add=True)  # 시작일
    end_date = models.DateTimeField()  # 만료일
    is_active = models.BooleanField(default=True)  # 현재 활성 상태 여부
    is_renew_scheduled = models.BooleanField(default=False)  # 자동 갱신 예약 여부

    class Meta:
        db_table = 'account_subscribe'
        app_label = 'subscribe'
