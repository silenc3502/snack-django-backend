from account_profile.repository.account_profile_repository_impl import AccountProfileRepositoryImpl
from account_profile.entity.account_profile import AccountProfile
from account_profile.service.account_profile_service import AccountProfileService

class AccountProfileServiceImpl(AccountProfileService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__repository = AccountProfileRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def createAccountProfile(
        self, account_id: int, account_name: str, account_nickname: str, phone_num: str,
        account_add: str, account_sex: str, account_birth: str, account_pay: dict, account_sub: bool
    ) -> AccountProfile:
        """새로운 AccountProfile을 생성한다."""
        profile = AccountProfile(
            account_id=account_id, account_name=account_name, account_nickname=account_nickname,
            phone_num=phone_num, account_add=account_add, account_sex=account_sex,
            account_birth=account_birth, account_pay=account_pay, account_sub=account_sub
        )
        return self.__repository.save(profile)

    def getProfileByAccountId(self, account_id: int) -> dict:
        """Account ID로 프로필을 찾는다."""
        return self.__repository.findByAccount(account_id)
