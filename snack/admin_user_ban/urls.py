from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admin_user_ban.controller.admin_user_ban_controller import AdminUserBanController

router = DefaultRouter()
router.register(r"admin-user-ban", AdminUserBanController, basename='admin-user-ban')

urlpatterns = [
    path("", include(router.urls)),
    path("ban", AdminUserBanController.as_view({"post": "banAccount"}), name="ban-account"),
    path("banned-list", AdminUserBanController.as_view({"get": "getBannedAccounts"}), name="get-banned-accounts"),
    path("unban/<int:account_id>", AdminUserBanController.as_view({"put": "unbanAccount"}), name="unban-account"),
]