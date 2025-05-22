from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from subscribe.entity.account_subscribe import AccountSubscribe
from subscribe.repository.account_subscribe_repository_impl import AccountSubscribeRepositoryImpl
from subscribe.repository.subscribe_repository_impl import SubscribeRepositoryImpl
from account.repository.account_repository_impl import AccountRepositoryImpl

class SubscribeServiceImpl:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__subscribeRepository = SubscribeRepositoryImpl.getInstance()
            cls.__instance.__accountSubscribeRepository = AccountSubscribeRepositoryImpl.getInstance()
            cls.__instance.__accountRepository = AccountRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def getAllSubscribes(self):
        return self.__subscribeRepository.findAllActive()

    def createSubscribe(self, subscriberId, subscribeId):

        subscriber = self.__accountRepository.findById(subscriberId)
        subscribe = self.__subscribeRepository.findById(subscribeId)
        if not subscriber:
            raise Exception("해당 사용자가 존재하지 않습니다.")
        if not subscribe:
            raise Exception("구독 플랜이 존재하지 않습니다.")

        # 기존 활성 구독 확인
        active_subscribe = self.__accountSubscribeRepository.findBySubscriberId(subscriberId)
        if active_subscribe and active_subscribe.is_active:
            raise Exception("이미 활성화된 구독이 존재합니다.")

        start_date = timezone.now()
        end_date = start_date + timedelta(days=subscribe.duration_days)

        accountSubscribe = AccountSubscribe(
            subscriber=subscriber,
            plan=subscribe,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            is_renew_scheduled=False
        )

        self.__accountSubscribeRepository.save(accountSubscribe)

    def getSubscriberStatus(self, subscriberId):
        sub = self.__accountSubscribeRepository.findBySubscriberId(subscriberId)
        if not sub or not sub.is_active or sub.end_date < timezone.now():
            return {"is_subscribed": False}
        return {
            "is_subscribed": True,
            "plan_type": sub.plan.plan_type,
            "end_date": sub.end_date,
        }

    # 구독 연장
    def extendSubscribe(self, subscriberId, days):
        accountSubscribe = self.__accountSubscribeRepository.findBySubscriberId(subscriberId)
        if not accountSubscribe:
            raise Exception("해당 유저의 구독이 존재하지 않습니다.")

        accountSubscribe.end_date += timedelta(days=days)
        self.__accountSubscribeRepository.save(accountSubscribe)

    # 자동 갱신 처리 (만료 예정 구독 자동 갱신)
    def renewScheduledSubscriptions(self):
        now = timezone.now()
        expiring_subscribes = self.__accountSubscribeRepository.findExpiringWithinDays(0)

        renewed_count = 0
        for sub in expiring_subscribes:
            if sub.is_active and sub.is_renew_scheduled:
                sub.start_date = now
                sub.end_date = now + timedelta(days=sub.plan.duration_days)
                self.__accountSubscribeRepository.save(sub)
                renewed_count += 1

        print(f"자동 갱신 완료: {renewed_count}건 갱신됨")
        return renewed_count

    #  만료된 구독 비활성화
    def deactivateExpiredSubscriptions(self):
        now = timezone.now()
        expiring_subscribes = self.__accountSubscribeRepository.findExpiringWithinDays(-1)

        deactivated_count = 0
        for sub in expiring_subscribes:
            if sub.is_active and sub.end_date < now:
                sub.is_active = False
                self.__accountSubscribeRepository.save(sub)
                deactivated_count += 1

        print(f"만료된 구독 비활성화: {deactivated_count}건 비활성화됨")
        return deactivated_count

    # 유저 구독 히스토리 조회
    def getSubscriberHistory(self, subscriberId):
        histories = self.__accountSubscribeRepository.findAllBySubscriberId(subscriberId)
        return [
            {
                "plan": h.plan.name,
                "start_date": h.start_date,
                "end_date": h.end_date,
                "is_active": h.is_active,
                "is_renew_scheduled": h.is_renew_scheduled
            }
            for h in histories
        ]

    # 구독 취소
    def cancelSubscribe(self, subscriberId):
        accountSubscribe = self.__accountSubscribeRepository.findBySubscriberId(subscriberId)
        if not accountSubscribe or not accountSubscribe.is_active:
            raise Exception("취소할 수 있는 활성화된 구독이 없습니다.")

        accountSubscribe.is_active = False
        accountSubscribe.is_renew_scheduled = False
        self.__accountSubscribeRepository.save(accountSubscribe)
        print(f"구독 취소 완료: {subscriberId}")

    # 구독 통계 조회 (전체 사용자 기준)
    def getSubscribeSummary(self):
        total_subscribers = self.__accountSubscribeRepository.countAll()
        active_subscribers = self.__accountSubscribeRepository.countActive()
        print(f"구독 통계 조회: 전체 {total_subscribers}, 활성 {active_subscribers}")
        return {
            "total_subscribers": total_subscribers,
            "active_subscribers": active_subscribers,
        }
