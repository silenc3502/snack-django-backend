from abc import ABC, abstractmethod

class AdminUserBanService(ABC):

    @abstractmethod
    def banAccountById(self, target_account_id: int, reason: str):
        pass

    @abstractmethod
    def getBannedAccounts(self):
        pass

    @abstractmethod
    def unbanAccountById(self, target_account_id: int):
        pass