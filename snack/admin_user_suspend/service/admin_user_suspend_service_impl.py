from account.entity.account import Account, AccountStatus
from account.entity.account_role_type import AccountRoleType
from account.entity.role_type import RoleType
from django.core.exceptions import ObjectDoesNotExist
from account.repository.account_repository_impl import AccountRepositoryImpl
from admin_user_suspend.repository.admin_user_suspend_repository_impl import AdminUserSuspendRepositoryImpl
from admin_user_suspend.service.admin_user_suspend_service import AdminUserSuspendService
from account.service.account_service import AccountService

from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils.timezone import now




class AdminUserSuspendServiceImpl(AdminUserSuspendService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__accountRepository = AccountRepositoryImpl.getInstance()
            cls.__instance.__adminUserSuspendRepository = AdminUserSuspendRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance


    def suspendAccountById(self, target_account_id: int, reason: str, duration: int = None):
        """사용자 계정 정지 처리"""
        target_account = self.__accountRepository.findById(target_account_id)
        if not target_account:
            raise ValueError("대상 사용자를 찾을 수 없습니다.")

        # 정지 기간 설정
        if duration is not None:
            try:
                duration = int(duration)  # 명시적 정수 변환
                if duration <= 0:
                    raise ValueError("정지 기간은 1 이상의 정수로 지정해야 합니다.")
                suspended_until = now() + timedelta(days=duration)
            except (ValueError, TypeError):
                raise ValueError("정지 기간은 1 이상의 정수로 지정해야 합니다.")
        else:
            suspended_until = None  # 영구 정지

        # 정지 처리
        target_account.account_status = AccountStatus.SUSPENDED.value
        target_account.suspension_reason = reason
        target_account.suspended_until = suspended_until

        # 상태 저장
        self.__adminUserSuspendRepository.updateSuspendedAccountStatus(target_account)
        return target_account

    def isSuspended(self, account_id: int):
        """사용자 계정 정지 상태 확인"""
        #  사용자 계정 조회
        account = self.__accountRepository.findById(account_id)
        if not account:
            raise ValueError("사용자를 찾을 수 없습니다.")

        # 정지된 상태인지 확인
        if account.account_status == AccountStatus.SUSPENDED.value:
            # 정지 만료일 확인 (기간이 남아있는지)
            if account.suspended_until:
                if account.suspended_until > now():
                    # 정지된 상태 유지
                    return True, f"정지된 계정입니다. 만료일: {account.suspended_until.strftime('%Y-%m-%d %H:%M:%S')}. 사유: {account.suspension_reason}"
                else:
                    #  만료일이 지났다면 자동 정지 해제
                    account.account_status = AccountStatus.ACTIVE.value
                    account.suspended_until = None
                    account.suspension_reason = None
                    self.__adminUserSuspendRepository.updateSuspendedAccountStatus(account)
                    return False, None  # 정지 해제

            #  무기한 정지된 경우
            return True, f"무기한 정지된 계정입니다. 사유: {account.suspension_reason}"

        # 정지되지 않은 사용자 (정상)
        return False, None

    def unsuspendAccountById(self, account_id: int):
        """사용자 정지 해제"""
        account = self.__accountRepository.findById(account_id)
        if not account:
            raise ValueError("사용자를 찾을 수 없습니다.")

        if account.account_status != AccountStatus.SUSPENDED.value:
            raise ValueError("정지된 사용자만 해제할 수 있습니다.")

        # 정지 상태 해제
        account.account_status = AccountStatus.ACTIVE.value
        account.suspended_until = None
        account.suspension_reason = None

        self.__adminUserSuspendRepository.updateSuspendedAccountStatus(account)

    def getSuspendedAccounts(self):
        """정지된 사용자 목록 조회"""
        try:
            return self.__adminUserSuspendRepository.findSuspendedAccounts()
        except Exception as e:
            raise ValueError(f"정지된 사용자 목록 조회 중 오류 발생: {str(e)}")

