from django.core.exceptions import ObjectDoesNotExist
from account_profile.entity.account_profile import AccountProfile
from account_profile.repository.account_profile_repository import AccountProfileRepository

class AccountProfileRepositoryImpl(AccountProfileRepository):
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

    def save(self, account_profile: AccountProfile):
        """AccountProfile을 저장한다."""
        account_profile.save()
        return account_profile

    def findByAccount(self, account_id: int):
        """Account ID를 이용해 AccountProfile을 찾는다."""
        try:
            profile = AccountProfile.objects.get(account_id=account_id)
            return {
                "account_id": profile.account.id,
                "account_name": profile.account_name,
                "account_nickname": profile.account_nickname,
                "phone_num": profile.phone_num,
                "account_add": profile.account_add,
                "account_sex": profile.account_sex,
                "account_birth": profile.account_birth.strftime('%Y-%m-%d') if profile.account_birth else None,
                "account_pay": profile.account_pay,
                "account_sub": profile.account_sub,
            }
        except ObjectDoesNotExist:
            return None
