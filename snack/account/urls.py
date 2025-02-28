from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account.controller.account_controller import AccountController

router = DefaultRouter()
router.register(r"account", AccountController, basename='account')

urlpatterns = [
    path("", include(router.urls)),
    path("create/", AccountController.as_view({"post": "createAccount"}), name="create-account"),
    path("get/<str:email>/", AccountController.as_view({"get": "getAccount"}), name="get-account"),
    path("update-last-used/<str:email>/", AccountController.as_view({"put": "updateLastUsed"}), name="update-last-used"),
]