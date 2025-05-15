from account_alarm.repository.account_alarm_repository_impl import AccountAlarmRepositoryImpl

class AccountAlarmServiceImpl:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.repository = AccountAlarmRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance


    def getUserAlarmList(self, account_id):
        return self.repository.findUnreadAlarmsById(account_id)


