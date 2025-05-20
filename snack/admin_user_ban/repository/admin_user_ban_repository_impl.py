from django.core.exceptions import ObjectDoesNotExist
from account.entity.account import Account, AccountStatus
from account.entity.account_role_type import AccountRoleType
from account.entity.role_type import RoleType
from admin_user_ban.repository.admin_user_ban_repository import AdminUserBanRepository


class AdminUserBanRepositoryImpl(AdminUserBanRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance


    def updateBannedAccountStatus(self, account: Account) -> None:
        """차단 사용자 계정 상태 업데이트"""
        update_fields = ['account_status', 'banned_reason', 'suspended_until', 'suspension_reason']
        account.save(update_fields=update_fields)


    def findBannedAccounts(self):
        """영구 탈퇴된 사용자 목록 조회"""
        return Account.objects.filter(
            account_status=AccountStatus.BANNED.value
        )