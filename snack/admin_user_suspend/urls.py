from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admin_user_suspend.controller.admin_user_suspend_controller import AdminUserSuspendController

router = DefaultRouter()
router.register(r"admin-user-suspend", AdminUserSuspendController, basename='admin-user-suspend')

urlpatterns = [
    path("", include(router.urls)),
    path("suspend", AdminUserSuspendController.as_view({"post": "suspendAccount"}), name="suspend-account"),
    path("suspended-list", AdminUserSuspendController.as_view({"get": "getSuspendedAccounts"}), name="get-suspended-accounts"),
    path("unsuspend/<int:account_id>", AdminUserSuspendController.as_view({"put": "unsuspendAccount"}), name="unsuspend-account"),
]