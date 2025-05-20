from abc import ABC, abstractmethod
from account.entity.account import Account


class AdminUserSuspendService(ABC):

    @abstractmethod
    def suspendAccountById(self, target_account_id: int, reason: str, duration: int = None):
        pass

    @abstractmethod
    def isSuspended(self, account_id: int):
        pass

    @abstractmethod
    def unsuspendAccountById(self, account_id: int):
        pass

    @abstractmethod
    def getSuspendedAccounts(self):
        pass