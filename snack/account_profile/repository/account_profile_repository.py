from abc import ABC, abstractmethod
from account_profile.entity.account_profile import AccountProfile

class AccountProfileRepository(ABC):
    @abstractmethod
    def save(self, account_profile: AccountProfile):
        """AccountProfile을 저장한다."""
        pass

    @abstractmethod
    def findByAccount(self, account_id: int):
        """Account ID를 이용해 AccountProfile을 찾는다."""
        pass

    @abstractmethod
    def findByNickname(self, account_nickname: str):
        """Account Nickname을 이용해 AccountProfile을 찾는다."""
        pass

    @abstractmethod
    def saveBoardAlarmStatus(self, account_id: int, alarm_board_status: bool):
        pass

    @abstractmethod
    def saveCommentAlarmStatus(self, account_id: int, alarm_comment_status: bool):
        pass