from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account_profile.controller.account_profile_controller import AccountProfileController

router = DefaultRouter()
router.register(r"account/profile", AccountProfileController, basename='account-profile')

urlpatterns = [
    path("", include(router.urls)),
    path("create/", AccountProfileController.as_view({"post": "createProfile"}), name="create-profile"),
    path("get/<str:email>/", AccountProfileController.as_view({"get": "getProfile"}), name="get-profile"),
]