from django.urls import path
from rest_framework.routers import DefaultRouter
from subscribe.controller.subscribe_controller import SubscribeController

# DRF Router 설정
router = DefaultRouter()
router.register(r'subscribe', SubscribeController, basename='subscribe')

urlpatterns = [
    path('list', SubscribeController.as_view({'get': 'requestSubscribeList'}), name='request-subscribe-list'),
    path('create', SubscribeController.as_view({'post': 'requestCreateSubscribe'}), name='request-create-subscribe'),
    path('status', SubscribeController.as_view({'get': 'requestGetSubscriber'}), name='request-get-subscriber'),
    path('renew', SubscribeController.as_view({'post': 'requestRenewScheduledSubscriptions'}), name='request-renew-scheduled-subscriptions'),
    path('deactivate', SubscribeController.as_view({'post': 'requestDeactivateExpiredSubscriptions'}), name='request-deactivate-expired-Subscriptions'),
    path('history', SubscribeController.as_view({'get': 'requestGetSubscriberHistory'}), name='request-get-subscriber-history'),
    path('cancel', SubscribeController.as_view({'post': 'requestCancelSubscribe'}), name='request-cancel-subscribe'),
]

# DRF router의 URL을 포함
urlpatterns += router.urls
