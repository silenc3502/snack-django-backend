from abc import ABC, abstractmethod


class googleOauthService(ABC):

    @abstractmethod
    def requestgoogleOauthLink(self):
        pass

    @abstractmethod
    def requestAccessToken(self, code):
        pass

    @abstractmethod
    def requestUserInfo(self, accessToken):
        pass
