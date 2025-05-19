from abc import ABC, abstractmethod
from account.entity.account import Account

class AdminUserSuspendRepository(ABC):

    @abstractmethod
    def updateSuspendedAccountStatus(self, account: Account) -> None:
        pass

    @abstractmethod
    def findSuspendedAccounts(self):
        pass