from account_alarm.repository.account_alarm_repository_impl import AccountAlarmRepositoryImpl
from account_profile.entity.account_profile import AccountProfile
from board.entity.board import Board
from comment.entity.comment import Comment
from account.entity.account import Account


class AccountAlarmServiceImpl:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__accountAlarmRepository = AccountAlarmRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance


    def getUserAllAlarmList(self, account_id):
        return self.__accountAlarmRepository.findUnreadAllAlarmsById(account_id)

    def getUserBoardAlarmList(self, account_id):
        return self.__accountAlarmRepository.findUnreadBoardAlarmsById(account_id)

    def getUserCommentAlarList(self, account_id):
        return self.__accountAlarmRepository.findUnreadCommentAlarmById(account_id)


    def readAlarm(self, alarm_id):
        return self.__accountAlarmRepository.saveReadAlarmById(alarm_id)


    def createBoardAlarm(self, board: Board, comment: Comment):
        return self.__accountAlarmRepository.saveBoardAlarm(board, comment)

    def createBoardReplyAlarm(self, board: Board, comment: Comment):
        return self.__accountAlarmRepository.saveBoardReplyAlarm(board, comment)



    def countUnreadAllAlarms(self, account_id):
        return self.__accountAlarmRepository.countUnreadAllAlarmsById(account_id)

    def countUnreadBoardAlarms(self, account_id):
        return self.__accountAlarmRepository.countUnreadBoardAlarmsById(account_id)

    def countUnreadCommentAlarms(self, account_id):
        return self.__accountAlarmRepository.countUnreadCommentAlarmsById(account_id)

