from django.db import transaction

from account.entity.account import Account
from account.repository.account_repository_impl import AccountRepositoryImpl
from account_profile.service.account_profile_service_impl import AccountProfileServiceImpl

from orders.repository.order_repository_impl import OrderRepositoryImpl


from payments.entity.payments import Payments
from payments.repository.payments_repository_impl import PaymentsRepositoryImpl
from payments.service.payments_service import PaymentsService
from dateutil.parser import isoparse


class PaymentsServiceImpl(PaymentsService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

            cls.__instance.__paymentsRepository = PaymentsRepositoryImpl.getInstance()
            cls.__instance.__accountRepository = AccountRepositoryImpl.getInstance()
            cls.__instance.__orderRepository = OrderRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def process(self, accountId, paymentKey, orderId, amount, orderInfoId):
        try:
            print(f"accountId: {accountId}")
            account = self.__accountRepository.findById(accountId)

            paymentRequestData = {
                "paymentKey": paymentKey,
                "orderId": orderId,
                "amount": amount,
            }
            print(f"paymentRequestData: {paymentRequestData}")

            paymentResult = self.__paymentsRepository.request(paymentRequestData)
            print(f"paymentResult: {paymentResult}")

            if paymentResult:
                ordersInfo = self.__orderRepository.findById(orderInfoId)

                # approvedAt 파싱 (tz-aware → naive)
                approved_at_raw = paymentResult.get('approvedAt')  # 예: "2025-05-21T17:37:41+09:00"
                approved_at = isoparse(approved_at_raw).replace(tzinfo=None)

                # 트랜잭션 처리
                with transaction.atomic():
                    payment = Payments(
                        account=account,
                        payment_key=paymentKey,
                        order_id=orderId,
                        orders_info=ordersInfo,
                        amount=amount,
                        provider=paymentResult.get('easyPay', {}).get('provider'),
                        method=paymentResult.get('method'),
                        paid_at=approved_at,
                        receipt_url=paymentResult.get('receipt', {}).get('url'),
                    )
                    self.__paymentsRepository.create(payment)  # 결제 정보 DB에 저장

                    # 결제 성공 시, 주문 상태 업데이트
                    if ordersInfo:
                        ordersInfo.status = "COMPLETED"  # 주문 상태를 완료로 변경
                        self.__orderRepository.save(ordersInfo)  # 주문 업데이트

                    # AccountProfile 업데이트
                    accountProfileService = AccountProfileServiceImpl.getInstance()
                    accountProfileService.updateProfile(accountId, {
                        "account_sub": True,
                        "account_pay": {
                            "order_id": orderId,
                            "amount": amount,
                            "method": paymentResult.get("method"),
                            "paid_at": approved_at.strftime("%Y-%m-%d %H:%M:%S")
                            }
                        })

                return paymentResult
            else:
                raise Exception("결제 요청 처리 실패")

        except Exception as e:
            print(f"결제 처리 중 오류 발생: {e}")
            return {"error": "Internal server error", "success": False}, 500
