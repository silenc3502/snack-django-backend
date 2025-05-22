from django.db import transaction
from orders.entity.orders import Orders
from orders.entity.order_status import OrderStatus
from orders.entity.order_item import OrderItems
from orders.repository.order_item_repository_impl import OrderItemRepositoryImpl
from account.repository.account_repository_impl import AccountRepositoryImpl
from subscribe.repository.subscribe_repository_impl import SubscribeRepositoryImpl
from subscribe.service.subscribe_service_impl import SubscribeServiceImpl
from orders.repository.order_repository_impl import OrderRepositoryImpl
from orders.service.order_service import OrderService


class OrderServiceImpl(OrderService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__orderRepository = OrderRepositoryImpl.getInstance()
            cls.__instance.__accountRepository = AccountRepositoryImpl.getInstance()
            cls.__instance.__orderItemRepository = OrderItemRepositoryImpl.getInstance()
            cls.__instance.__subscribeRepository = SubscribeRepositoryImpl.getInstance()
            cls.__instance.__subscribeService = SubscribeServiceImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @transaction.atomic
    def createOrder(self, accountId, items, total):
        account = self.__accountRepository.findById(accountId)

        if not account:
            raise Exception(f"Account id {accountId} 존재하지 않음.")

            # 2. 총 금액 검증
        if not isinstance(total, (int, float)) or total <= 0:
            raise Exception("유효하지 않은 총 금액입니다.")

            # 3. 주문 항목 검증
        if not items or not isinstance(items, list):
            raise Exception("유효하지 않은 주문 항목입니다.")

        order = Orders(
            account=account,
            total_amount=total,
            status=OrderStatus.PENDING,
        )
        order = self.__orderRepository.save(order)
        print(f"order 생성: {order}")

        orderItemList = []
        for item in items:
            subscribe = self.__subscribeRepository.findById(item["id"])
            if not subscribe:
                raise Exception(f"Subscribe ID {item['id']} 존재하지 않음.")
            self.__subscribeService.createSubscribe(accountId, subscribe.id)

            orderItem = OrderItems(
                orders=order,
                plan=subscribe,
                quantity=1,
                price=subscribe.price
            )
            orderItemList.append(orderItem)

        if orderItemList:
            self.__orderItemRepository.bulkCreate(orderItemList)

        order.status = OrderStatus.COMPLETED
        self.__orderRepository.save(order)

        return order.getId()
