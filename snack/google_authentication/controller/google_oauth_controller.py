import uuid

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.status import HTTP_200_OK

from account.service.account_service_impl import AccountServiceImpl
from account_profile.service.account_profile_service_impl import AccountProfileServiceImpl
from google_authentication.serializer.google_oauth_access_token_serializer import googleOauthAccessTokenSerializer
from google_authentication.service.google_oauth_service_impl import googleOauthServiceImpl
from redis_cache.service.redis_cache_service_impl import RedisCacheServiceImpl
from account.entity.role_type import RoleType

class googleOauthController(viewsets.ViewSet):
    googleOauthService = googleOauthServiceImpl.getInstance()
    accountService = AccountServiceImpl.getInstance()
    accountProfileService = AccountProfileServiceImpl.getInstance()
    redisCacheService = RedisCacheServiceImpl.getInstance()

    def requestgoogleOauthLink(self, request):
        url = self.googleOauthService.requestgoogleOauthLink()

        return JsonResponse({"url": url}, status=status.HTTP_200_OK)

    def requestAccessToken(self, request):
        serializer = googleOauthAccessTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        print(f"code: {code}")

        try:
            tokenResponse = self.googleOauthService.requestAccessToken(code)
            accessToken = tokenResponse['access_token']
            print(f"accessToken: {accessToken}")

            with transaction.atomic():
                userInfo = self.googleOauthService.requestUserInfo(accessToken)
                nickname = userInfo.get('properties', {}).get('nickname', '')
                email = userInfo.get('google_account', {}).get('email', '')
                account_path = "google"
                role_type = RoleType.USER
                phone_num =""
                add = ""
                sex = ""
                birth= None
                pay = ""
                sub = False
                print(f"email: {email}, nickname: {nickname}")

                account = self.accountService.checkEmailDuplication(email)
                print(f"account: {account}")

                if account is None:
                    account = self.accountService.createAccount(email, account_path, role_type)
                    print(f"account: {account}")

                    accountProfile = self.accountProfileService.createAccountProfile(
                        account.id, nickname, nickname, phone_num, add, sex, birth, pay, sub
                    )
                    print(f"accountProfile: {accountProfile}")

                self.accountService.updateLastUsed(account.id)

                userToken = self.__createUserTokenWithAccessToken(account, accessToken)
                print(f"userToken: {userToken}")

            return JsonResponse({'userToken': userToken})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def requestUserToken(self, request):
        access_token = request.data.get('access_token')  # 클라이언트에서 받은 access_token
        email = request.data.get('email')  # 클라이언트에서 받은 email
        nickname = request.data.get('nickname')  # 클라이언트에서 받은 nickname

        if not access_token:
            return JsonResponse({'error': 'Access token is required'}, status=400)

        if not email or not nickname:
            return JsonResponse({'error': 'Email and nickname are required'}, status=400)

        try:
            # 이메일을 기반으로 계정을 찾거나 새로 생성합니다.
            account = self.accountService.checkEmailDuplication(email)
            if account is None:
                account = self.accountService.createAccount(email)
                accountProfile = self.accountProfileService.createAccountProfile(
                    account.getId(), nickname
                )

            # 사용자 토큰 생성 및 Redis에 저장
            userToken = self.__createUserTokenWithAccessToken(account, access_token)

            return JsonResponse({'userToken': userToken})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def __createUserTokenWithAccessToken(self, account, accessToken):
        try:
            userToken = str(uuid.uuid4())
            self.redisCacheService.storeKeyValue(account.getId(), accessToken)
            self.redisCacheService.storeKeyValue(userToken, account.getId())

            return userToken

        except Exception as e:
            print('Redis에 토큰 저장 중 에러:', e)
            raise RuntimeError('Redis에 토큰 저장 중 에러')