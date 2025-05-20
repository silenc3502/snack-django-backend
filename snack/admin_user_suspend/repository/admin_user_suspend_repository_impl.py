from django.core.exceptions import ObjectDoesNotExist
from account.entity.account import Account, AccountStatus
from account.entity.account_role_type import AccountRoleType
from account.entity.role_type import RoleType
from admin_user_suspend.repository.admin_user_suspend_repository import AdminUserSuspendRepository
from datetime import datetime, timedelta
from django.utils.timezone import now


class AdminUserSuspendRepositoryImpl(AdminUserSuspendRepository):
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

    def updateSuspendedAccountStatus(self, account: Account) -> None:
        """사용자 계정 상태 업데이트"""
        update_fields = ['account_status', 'suspension_reason', 'suspended_until']
        account.save(update_fields=update_fields)


    def findSuspendedAccounts(self):
        """정지된 사용자 목록을 DB에서 조회"""
        return Account.objects.filter(
            account_status=1,
            suspended_until__gt=now()
        ) | Account.objects.filter(
            account_status=1,
            suspended_until__isnull=True
        )
        # """정지된 사용자 목록을 DB에서 조회"""
        # return Account.objects.filter(account_status=1, suspended_until__gt=now()) # 현재 시점보다 정지 만료일이 큰 사용자만 조회
        #
