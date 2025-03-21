import uuid

from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets, status
from datetime import datetime

from account.service.account_service_impl import AccountServiceImpl
from account_profile.service.account_profile_service_impl import AccountProfileServiceImpl
from naver_authentication.service.naver_oauth_service_impl import NaverOauthServiceImpl
from redis_cache.service.redis_cache_service_impl import RedisCacheServiceImpl
from account.entity.role_type import RoleType

class NaverOauthController(viewsets.ViewSet):
    naverOauthService = NaverOauthServiceImpl.getInstance()
    accountService = AccountServiceImpl.getInstance()
    accountProfileService = AccountProfileServiceImpl.getInstance()
    redisCacheService = RedisCacheServiceImpl.getInstance()

    # 1. 네이버 로그인 URL 요청
    def requestNaverOauthLink(self, request):
        url = self.naverOauthService.requestNaverOauthLink()
        return JsonResponse({"url": url}, status=status.HTTP_200_OK)

    # 2. 네이버 Access Token 요청 및 사용자 정보 가져오기
    def requestAccessToken(self, request):
        code = request.data.get('code')
        state = request.data.get('state')

        if not code:
            return JsonResponse({'error': 'Authorization code is required'}, status=400)

        try:
            tokenResponse = self.naverOauthService.requestAccessToken(code, state)
            accessToken = tokenResponse['access_token']

            with transaction.atomic():
                userInfo = self.naverOauthService.requestUserInfo(accessToken)

                print(f"네이버 사용자 정보: {userInfo}")
                email = userInfo.get('response', {}).get('email', '')
                nickname = userInfo.get('response', {}).get('nickname', '')
                #profile_image = userInfo.get('response', {}).get('profile_image', '')
                name = userInfo.get('response', {}).get('name', '')
                account_path = "Naver"
                role_type = RoleType.USER
                phone_num = userInfo.get('response', {}).get('mobile', '')
                address = ""
                gender = userInfo.get('response', {}).get('gender', '')
                birthyear = userInfo.get('response', {}).get('birthyear', '')
                birthday = userInfo.get('response', {}).get('birthday', '')
                payment = ""
                subscribed = False

                birth = None
                if birthday and birthyear:
                    birth = f"{birthyear}-{birthday}"
                    try:
                        birth = datetime.strptime(birth, "%Y-%m-%d").date()
                    except ValueError:
                        birth = None
                    
                print(birth)

                conflict_message = self.accountService.checkAccountPath(email, account_path)
                if conflict_message:
                    return JsonResponse({'success': False, 'error_message': conflict_message}, status = 210)
                # 기존 계정 확인
                account = self.accountService.checkEmailDuplication(email)

                # 새 계정 및 프로필 생성
                if account is None:
                    account = self.accountService.createAccount(email, account_path, role_type)
                    accountProfile = self.accountProfileService.createAccountProfile(
                        account.id, name, nickname, phone_num, address, gender, birth, payment, subscribed
                    )

                # age = None
                # if accountProfile:
                #     age = accountProfile.account_age
                # print(age)
                # 마지막 로그인 시간 업데이트
                self.accountService.updateLastUsed(account.id)

                # 사용자 토큰 생성 및 Redis 저장
                userToken = self.__createUserTokenWithAccessToken(account, accessToken)
                print(userToken)
                abcToken = self.redisCacheService.storeKeyValue(account.email, account.id)
                print(abcToken)
            return JsonResponse({'userToken': userToken})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # 3. 사용자 토큰 요청
    def requestUserToken(self, request):
        access_token = request.data.get('access_token')
        email = request.data.get('email')
        nickname = request.data.get('nickname')
        account_path = "Naver"
        role_type = RoleType.USER

        phone_num = request.data.get('phone_num', "")
        address = request.data.get('address', "")
        gender = request.data.get('gender', "")
        birthyear = request.data.get('birthyear', "")
        birthday = request.data.get('birthday', "")
        payment = request.data.get('payment', "")
        subscribed = request.data.get('subscribed', False)

        # 생년월일 데이터 변환
        birth = None
        if birthday and birthyear:
            birth = f"{birthyear}-{birthday}"
            try:
                birth = datetime.strptime(birth, "%Y-%m-%d").date()
            except ValueError:
                birth = None

        if not access_token:
            return JsonResponse({'error': 'Access token is required'}, status=400)

        if not email or not nickname:
            return JsonResponse({'error': 'Email and nickname are required'}, status=400)

        try:
            # 🔹 가입된 OAuth 경로 충돌 체크
            conflict_message = self.accountService.checkAccountPath(email, account_path)
            if conflict_message:
                return JsonResponse({'success': False, 'error_message': conflict_message}, status = 200)

            with transaction.atomic():  # 🔥 Atomic 트랜잭션 시작
                # 🔹 이메일 중복 검사
                account = self.accountService.checkEmailDuplication(email)
                print(f"account: {account}")

                if account is None:
                    # 🔹 새 계정 생성
                    account = self.accountService.createAccount(email, account_path, role_type)
                    print(f"account created: {account}")

                    # 🔹 새 계정 프로필 생성
                    accountProfile = self.accountProfileService.createAccountProfile(
                        account.id, nickname, nickname, phone_num, address, gender, birth, payment, subscribed
                    )
                    print(f"accountProfile: {accountProfile}")

                # 🔹 마지막 로그인 시간 업데이트
                self.accountService.updateLastUsed(account.id)

                # 🔹 사용자 토큰 생성 및 Redis 저장
                userToken = self.__createUserTokenWithAccessToken(account, access_token)
                print(f"userToken: {userToken}")

            return JsonResponse({'userToken': userToken})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


    # 4. Redis를 활용한 사용자 토큰 저장
    def __createUserTokenWithAccessToken(self, account, accessToken):
        try:
            userToken = f"naver-{uuid.uuid4()}"
            self.redisCacheService.storeKeyValue(account.getId(), accessToken)
            self.redisCacheService.storeKeyValue(userToken, account.getId())

            return userToken

        except Exception as e:
            print('Redis에 토큰 저장 중 에러:', e)
            raise RuntimeError('Redis에 토큰 저장 중 에러')
