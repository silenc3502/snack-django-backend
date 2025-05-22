from datetime import timedelta
from django.utils import timezone

from subscribe.entity.account_subscribe import AccountSubscribe
from subscribe.repository.account_subscribe_repository import AccountSubscribeRepository


class AccountSubscribeRepositoryImpl(AccountSubscribeRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        # 싱글톤 인스턴스 반환
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def findBySubscriberId(self, subscriberId):
        # 유저 ID 기준 가장 최근 구독 정보 1건 반환
        return AccountSubscribe.objects.filter(subscriber__id=subscriberId).order_by('-end_date').first()

    def save(self, accountSubscribe):
        accountSubscribe.save()
        return accountSubscribe

    def findExpiringWithinDays(self, days):
        # 현재 시점 기준 X일 내에 만료되는 구독 리스트 반환
        threshold_date = timezone.now() + timedelta(days=days)
        return AccountSubscribe.objects.filter(end_date__lte=threshold_date, is_active=True)

    def findAllBySubscriberId(self, subscriberId):
        return AccountSubscribe.objects.filter(subscriber__id=subscriberId).order_by('-start_date')

    def countAll(self):
        return AccountSubscribe.objects.count()

    def countActive(self):
        return AccountSubscribe.objects.filter(is_active=True).count()

    def totalRevenue(self):
        from django.db.models import Sum
        return AccountSubscribe.objects.filter(is_active=True).aggregate(
            revenue=Sum('plan__price')
        )['revenue'] or 0