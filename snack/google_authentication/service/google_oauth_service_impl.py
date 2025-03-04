from google_authentication.repository.google_oauth_repository_impl import googleOauthRepositoryImpl
from google_authentication.service.google_oauth_service import googleOauthService


class googleOauthServiceImpl(googleOauthService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

            cls.__instance.__googleOauthRepository = googleOauthRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def requestgoogleOauthLink(self):
        return self.__googleOauthRepository.getOauthLink()

    def requestAccessToken(self, code):
        return self.__googleOauthRepository.getAccessToken(code)

    def requestUserInfo(self, accessToken):
        return self.__googleOauthRepository.getUserInfo(accessToken)
