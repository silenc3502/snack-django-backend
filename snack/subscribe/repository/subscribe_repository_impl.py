from subscribe.entity.subscribe import Subscribe
from subscribe.repository.subscribe_repository import SubscribeRepository

# SubscribeRepository 인터페이스의 실제 구현체 (싱글톤 패턴 적용)
class SubscribeRepositoryImpl(SubscribeRepository):
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

    def findById(self, subscribeId):
        try:
            return Subscribe.objects.get(id=subscribeId)
        except Subscribe.DoesNotExist:
            return None

    def findAllActive(self):
        return Subscribe.objects.filter(is_active=True)

    def save(self, subscribe):
        subscribe.save()
        return subscribe


