from django.core.exceptions import ObjectDoesNotExist
from account.repository.account_repository_impl import AccountRepositoryImpl
from account.service.account_service import AccountService
from admin_user_ban.service.admin_user_ban_service import AdminUserBanService
from admin_user_ban.repository.admin_user_ban_repository_impl import AdminUserBanRepositoryImpl
from account.entity.account import Account, AccountStatus
from account.entity.account_role_type import AccountRoleType
from account.entity.role_type import RoleType
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils.timezone import now


class AdminUserBanServiceImpl(AdminUserBanService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__accountRepository = AccountRepositoryImpl.getInstance()
            cls.__instance.__adminUserBanRepository = AdminUserBanRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance



    def banAccountById(self, target_account_id: int, reason: str):
        """사용자 계정 차단 (영구 탈퇴) 처리"""
        target_account = self.__accountRepository.findById(target_account_id)
        if not target_account:
            raise ValueError("대상 사용자를 찾을 수 없습니다.")

        # 이미 정지된 사용자인 경우에도 무시하고 바로 차단 처리
        target_account.account_status = AccountStatus.BANNED.value
        target_account.banned_reason = reason

        # 정지 상태 관련 필드 초기화
        target_account.suspended_until = None
        target_account.suspension_reason = None

        # 상태 저장 (차단 사용자)
        self.__adminUserBanRepository.updateBannedAccountStatus(target_account)
        return target_account

    def getBannedAccounts(self):
        """영구 탈퇴된 사용자 목록 조회"""
        try:
            return self.__adminUserBanRepository.findBannedAccounts()
        except Exception as e:
            raise ValueError(f"차단된 사용자 목록 조회 중 오류 발생: {str(e)}")

    def unbanAccountById(self, target_account_id: int):
        """사용자 영구탈퇴 해제"""
        target_account = self.__accountRepository.findById(target_account_id)
        if not target_account:
            raise ValueError("대상 사용자를 찾을 수 없습니다.")

        if target_account.account_status != 4:
            raise ValueError("대상 사용자가 영구탈퇴된 상태가 아닙니다.")

        # 영구탈퇴 해제
        target_account.account_status = 0  # Active 상태로 변경
        target_account.banned_reason = None  # 차단 사유 삭제
        self.__adminUserBanRepository.updateBannedAccountStatus(target_account)

