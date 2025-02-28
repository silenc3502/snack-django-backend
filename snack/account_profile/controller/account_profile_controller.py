from django.http import JsonResponse
from rest_framework import viewsets, status

from account_profile.service.account_profile_service_impl import AccountProfileServiceImpl
from redis_cache.service.redis_cache_service_impl import RedisCacheServiceImpl


class AccountProfileController(viewsets.ViewSet):
    __profileService = AccountProfileServiceImpl.getInstance()
    redisCacheService = RedisCacheServiceImpl.getInstance()

    def createProfile(self, request):
        """AccountProfile을 생성하는 엔드포인트"""
        postRequest = request.data
        email = postRequest.get("email")

        # Redis에서 account_id 가져오기
        account_id = self.redisCacheService.getValueByKey(email)

        if not account_id:
            return JsonResponse({"error": "해당 이메일에 대한 계정 정보를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        profile = self.__profileService.createAccountProfile(
            account_id=account_id,
            account_name=postRequest.get("account_name"),
            account_nickname=postRequest.get("account_nickname"),
            phone_num=postRequest.get("phone_num"),
            account_add=postRequest.get("account_add"),
            account_sex=postRequest.get("account_sex"),
            account_birth=postRequest.get("account_birth"),
            account_pay=postRequest.get("account_pay"),
            account_sub=postRequest.get("account_sub")
        )
        return JsonResponse({"success": True, "profile_id": profile.account.id}, status=status.HTTP_201_CREATED)

    def getProfile(self, request, email):
        """이메일을 이용하여 AccountProfile을 조회하는 엔드포인트"""
        account_id = self.redisCacheService.getValueByKey(email)

        if not account_id:
            return JsonResponse({"error": "해당 이메일에 대한 계정 정보를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        profile = self.__profileService.getProfileByAccountId(account_id)

        if not profile:
            return JsonResponse({"error": "프로필을 찾을 수 없습니다", "success": False}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({
            "account_id": profile["account_id"],
            "account_name": profile["account_name"],
            "account_nickname": profile["account_nickname"],
            "phone_num": profile["phone_num"],
            "account_add": profile["account_add"],
            "account_sex": profile["account_sex"],
            "account_birth": profile["account_birth"],
            "account_pay": profile["account_pay"],
            "account_sub": profile["account_sub"],
            "success": True
        }, status=status.HTTP_200_OK)
