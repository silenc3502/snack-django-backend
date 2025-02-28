from django.core.exceptions import ObjectDoesNotExist
from account.repository.account_repository_impl import AccountRepositoryImpl
from account.service.account_service import AccountService
from account.entity.account import Account
from account.entity.account_role_type import AccountRoleType
from account.entity.role_type import RoleType

class AccountServiceImpl(AccountService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__accountRepository = AccountRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def createAccount(self, email: str, account_path: str, role_type: str) -> Account:
        """새로운 계정을 생성한다."""
        try:
            defaultRoleType = AccountRoleType.objects.get(role_type=role_type)
        except ObjectDoesNotExist:
            defaultRoleType = AccountRoleType(role_type=role_type)
            defaultRoleType.save()

        account = Account(email=email, role_type=defaultRoleType, account_path=account_path)
        return self.__accountRepository.save(account)

    def checkEmailDuplication(self, email: str) -> bool:
        """이메일 중복 확인"""
        try:
            return self.__accountRepository.findByEmail(email) 
        except ObjectDoesNotExist:
            return None

    def findAccountById(self, account_id: int) -> Account:
        """Account ID로 계정을 찾는다."""
        return self.__accountRepository.findById(account_id)

    def updateLastUsed(self, account_id: int):
        """로그인 시 마지막 접속 날짜를 업데이트 하고 변경된 데이터를 반환한다."""
        updated_account = self.__accountRepository.updateLastUsed(account_id)
        if updated_account:
            print(f"로그인 시 account_used_date 갱신 완료: {updated_account.account_used_date}")
        else:
            print(f"계정 {account_id}를 찾을 수 없음")
        return updated_account