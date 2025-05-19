from abc import ABC, abstractmethod
from account.entity.account import Account

class AdminUserBanRepository(ABC):

    @abstractmethod
    def updateBannedAccountStatus(self, account: Account) -> None:
        pass

    @abstractmethod
    def findBannedAccounts(self):
        pass