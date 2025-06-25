import base64
import requests
from snack import settings
from payments.repository.payments_repository import PaymentsRepository


class PaymentsRepositoryImpl(PaymentsRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

            cls.__instance.paymentApiBaseUrl = settings.TOSS_PAYMENTS["TOSS_PAYMENTS_BASE_URL"]
            cls.__instance.paymentApiSecretKey = settings.TOSS_PAYMENTS["TOSS_PAYMENTS_SECRET_KEY"]

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def create(self, payments):
        try:
            payments.save()
            return payments
        except Exception as e:
            print(f"결제 정보 저장 중 오류 발생: {e}")
            return None

    def request(self, paymentRequestData):
        try:
            headers = {
                "Authorization": f"Basic {self.__getEncryptedSecretKey()}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                f"{self.paymentApiBaseUrl}",
                headers=headers,
                json=paymentRequestData
            )


            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API 요청 실패: {response.json().get('message')}")

        except Exception as e:
            print(f"결제 요청 중 오류 발생: {e}")
            return None

    def __getEncryptedSecretKey(self):
        # 시크릿 키 암호화
        secretKey = self.paymentApiSecretKey
        secretKeyBytes = (secretKey + ":").encode('utf-8')  # ':'을 추가하여 인코딩 준비
        encryptedSecretKey = base64.b64encode(secretKeyBytes).decode('utf-8')  # Base64로 인코딩 후 문자열로 변환
        return encryptedSecretKey