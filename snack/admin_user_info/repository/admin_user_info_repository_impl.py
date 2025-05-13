from account.entity.account import Account
from account_profile.entity.account_profile import AccountProfile

class AdminUserInfoRepositoryImpl:
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


    def findUserById(self, user_id):
        user = (
            Account.objects
            .select_related('accountprofile')  # AccountProfile과 조인
            .filter(id=user_id)
            .values(
                'id', 'email', 'account_status', 'account_path', 'account_register',
                'accountprofile__account_name', 'accountprofile__account_nickname',
                'accountprofile__phone_num', 'accountprofile__account_add',
                'accountprofile__account_sex', 'accountprofile__account_birth',
                'accountprofile__account_pay', 'accountprofile__account_sub'
            )
            .first()
        )
        if not user:
            return None

        return self.__formatUserInfo(user)

    def __formatUserInfo(self, user):
        return {
            "id": user['id'],
            "email": user['email'],
            "account_status": user['account_status'],
            "account_path": user['account_path'],
            "created_at": user['account_register'],
            "profile": {
                "name": user.get('accountprofile__account_name'),
                "nickname": user.get('accountprofile__account_nickname'),
                "phone_num": user.get('accountprofile__phone_num'),
                "address": user.get('accountprofile__account_add'),
                "gender": user.get('accountprofile__account_sex'),
                "birth": user.get('accountprofile__account_birth'),
                "payment": user.get('accountprofile__account_pay'),
                "subscribed": user.get('accountprofile__account_sub')
            }
        }
