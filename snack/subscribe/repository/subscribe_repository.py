from abc import ABC, abstractmethod

# 구독 상품에 대한 데이터 접근 인터페이스
class SubscribeRepository(ABC):

    @abstractmethod
    def findById(self, subscribeId):
        # ID로 subscribe 조회
        pass

    @abstractmethod
    def findAllActive(self):
        # 사용 가능한 모든 subscribe 목록 조회
        pass

    @abstractmethod
    def save(self, subscribe):
        # subscribe 저장 또는 수정
        pass