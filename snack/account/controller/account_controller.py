from django.http import JsonResponse
from rest_framework import viewsets, status

from account.service.account_service_impl import AccountServiceImpl
from redis_cache.service.redis_cache_service_impl import RedisCacheServiceImpl


class AccountController(viewsets.ViewSet):
    __accountService = AccountServiceImpl.getInstance()
    redisCacheService = RedisCacheServiceImpl.getInstance()

    def createAccount(self, request):
        """새로운 계정을 생성하는 엔드포인트"""
        postRequest = request.data
        email = postRequest.get("email")
        account_path = postRequest.get("account_path")
        role_type = postRequest.get("role_type", "user")  # 기본값: user

        if not email or not account_path:
            return JsonResponse({"error": "email과 account_path가 필요합니다", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        if self.__accountService.checkEmailDuplication(email):
            return JsonResponse({"error": "이미 존재하는 이메일입니다", "success": False}, status=status.HTTP_409_CONFLICT)

        account = self.__accountService.createAccount(email, account_path, role_type)

        # Redis에 계정 ID 저장 (key: email, value: account_id)
        self.redisCacheService.storeKeyValue(email, account.id)

        return JsonResponse({"success": True, "account_id": account.id}, status=status.HTTP_201_CREATED)

    def getAccount(self, request, email):
        """이메일을 기반으로 Redis에서 계정 ID를 찾아서 조회"""
        account_id = self.redisCacheService.getValueByKey(email)

        if not account_id:
            return JsonResponse({"error": "해당 이메일에 대한 계정 정보를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        account = self.__accountService.findAccountById(account_id)
        if not account:
            return JsonResponse({"error": "계정을 찾을 수 없습니다", "success": False}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({
            "account_id": account.id,
            "email": account.email,
            "role_type": account.role_type.role_type,
            "account_register": account.account_register.strftime('%Y-%m-%d %H:%M:%S'),
            "account_used_date": account.account_used_date.strftime('%Y-%m-%d %H:%M:%S'),
            "account_path": account.account_path,
            "is_active": account.is_active,
            "success": True
        }, status=status.HTTP_200_OK)

    def updateLastUsed(self, request, email):
        """이메일 기반으로 Redis에서 account_id를 가져와 마지막 로그인 날짜 업데이트"""
        account_id = self.redisCacheService.getValueByKey(email)

        if not account_id:
            return JsonResponse({"error": "해당 이메일에 대한 계정 정보를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        updated_account = self.__accountService.updateLastUsed(account_id)

        if not updated_account:
            return JsonResponse({"error": "계정을 찾을 수 없습니다", "success": False}, status=status.HTTP_404_NOT_FOUND)

        self.redisCacheService.storeKeyValue(email, account_id)
        
        return JsonResponse({
            "message": "최근 사용 날짜가 업데이트되었습니다.",
            "last_used_date": updated_account.account_used_date.strftime('%Y-%m-%d %H:%M:%S'),
            "success": True
        }, status=status.HTTP_200_OK)


    def requestEmail(self, request):
        """Nuxt의 이메일 요청 처리하고 반환"""
        postRequest = request.data
        userToken = postRequest.get("userToken")

        # userToken이 없으면 400 오류 반환
        if not userToken:
            return JsonResponse({"error": "userToken이 필요합니다", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:

            account_id = self.redisCacheService.getValueByKey(userToken)

            if not account_id:

                return JsonResponse({"error": "해당 account_id가 없습니다", "success": False},status=status.HTTP_404_NOT_FOUND)

            foundEmail = self.__accountService.findEmail(account_id)

            if foundEmail is None:
                # 이메일 못찾음
                return JsonResponse({"error": "이메일을 찾을 수 없습니다", "success": False}, status=status.HTTP_404_NOT_FOUND)

            # 이메일 찾음
            return JsonResponse({"email": foundEmail, "success": True}, status=status.HTTP_200_OK)

        except Exception as e:

            print(f"서버 오류 발생: {e}")
            return JsonResponse({"error": "서버 내부 오류", "success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
