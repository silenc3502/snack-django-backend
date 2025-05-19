from django.http import JsonResponse
from rest_framework import viewsets, status
from datetime import datetime, timedelta
from account.service.account_service_impl import AccountServiceImpl
from admin_user_suspend.service.admin_user_suspend_service_impl import AdminUserSuspendServiceImpl
from redis_cache.service.redis_cache_service_impl import RedisCacheServiceImpl
from rest_framework.response import Response


from datetime import datetime, timedelta
from django.utils.timezone import now

class AdminUserSuspendController(viewsets.ViewSet):
    __accountService = AccountServiceImpl.getInstance()
    __adminUserSuspendService = AdminUserSuspendServiceImpl.getInstance()
    redisCacheService = RedisCacheServiceImpl.getInstance()

    # 이메일 복호화
    def __decryptEmail(self, account):
        try:
            decrypted_email = account.get_decrypted_email()
            print(f"복호화된 이메일: {decrypted_email}")
            return decrypted_email
        except Exception as e:
            print(f"[ERROR] 이메일 복호화 실패: {str(e)}")
            return account.email  # fallback: 암호화 된 그대로 반환

    # 관리자 로그인, 권한 확인
    def __checkAdminSuspendPermission(self, user_token):
        # 유저 토큰 확인
        if not user_token:
            return None, JsonResponse({"error": "userToken이 필요합니다", "success": False},
                                      status=status.HTTP_400_BAD_REQUEST)

        # 관리자 계정 로그인 확인
        admin_account_id = self.redisCacheService.getValueByKey(user_token)
        if not admin_account_id:
            return None, JsonResponse({"error": "로그인이 필요합니다.", "success": False}, status=status.HTTP_401_UNAUTHORIZED)

        # 관리자 권한 확인
        admin_account = self.__accountService.findAccountById(admin_account_id)
        if not admin_account or admin_account.role_type.role_type != 'ADMIN':
            return None, JsonResponse({"error": "관리자 권한이 필요합니다.", "success": False}, status=status.HTTP_403_FORBIDDEN)

        return admin_account, None

    #  관리자 -사용자 계정 정지 요청(SUSPEND)
    def suspendAccount(self, request):
        user_token = request.headers.get("userToken")
        target_account_id = request.data.get("target_account_id")
        reason = request.data.get("reason", "정지 사유")
        duration = request.data.get("duration")  # 정지 기간 일수 (정수)

        admin_account, error_response = self.__checkAdminSuspendPermission(user_token)
        if error_response:
            return error_response  # 관리자 로그인, 권한 확인

        # 대상 사용자 확인
        target_account = self.__accountService.findAccountById(target_account_id)
        if not target_account:
            return Response({"error": "대상 사용자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        # 영구 탈퇴 여부 확인
        if target_account.account_status == 4:
            return JsonResponse({"error": "대상 사용자는 영구 탈퇴 상태 입니다.", "success": False},
                                status=status.HTTP_400_BAD_REQUEST)

        # 대상 사용자 정지 상태 확인 (이미 정지된 사용자 확인)
        is_suspended, message = self.__adminUserSuspendService.isSuspended(target_account_id)
        if is_suspended:
            return Response({"error": message, "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            suspended_account = self.__adminUserSuspendService.suspendAccountById(
                target_account_id=target_account_id,
                reason=reason,
                duration=int(duration) if duration else None
            )
            decrypted_email = self.__decryptEmail(suspended_account)

            return Response({
                "success": True,
                "message": f"사용자 {decrypted_email} (ID: {suspended_account.id})이 정지되었습니다.",
                "reason": suspended_account.suspension_reason,
                "suspended_until": suspended_account.suspended_until.strftime(
                    '%Y-%m-%d %H:%M:%S') if suspended_account.suspended_until else "무기한 정지"
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e), "success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # 관리자 -정지된 사용자 계정을 해제
    def unsuspendAccount(self, request, account_id):
        user_token = request.headers.get("userToken")
        target_account = self.__accountService.findAccountById(account_id)  # URL에서 받아온 account_id 사용

        if not target_account:
            return JsonResponse({"error": "대상 사용자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        admin_account, error_response = self.__checkAdminSuspendPermission(user_token)
        if error_response:
            return error_response

        # 정지 여부 확인
        if target_account.account_status != 1:
            return JsonResponse({"error": "대상 사용자가 계정 정지 된 상태가 아닙니다.", "success": False},
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            self.__adminUserSuspendService.unsuspendAccountById(account_id)
            return Response({"success": True, "message": "사용자 계정의 정지가 해제되었습니다."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # 관리자 -정지된 사용자 목록 조회
    def getSuspendedAccounts(self, request):
        user_token = request.headers.get("userToken")

        admin_account, error_response = self.__checkAdminSuspendPermission(user_token)
        if error_response:
            return error_response

        try:
            suspended_accounts = self.__adminUserSuspendService.getSuspendedAccounts()
            result = []

            for account in suspended_accounts:
                try:
                    decrypted_email = self.__decryptEmail(account)
                except Exception as e:
                    print(f"[ERROR] 이메일 복호화 실패: {str(e)}")
                    decrypted_email = account.email  # 복호화 실패 시 원래 이메일 유지

                result.append({
                    "id": account.id,
                    "email": decrypted_email,
                    "reason": account.suspension_reason,
                    "suspended_until": account.suspended_until.strftime(
                        '%Y-%m-%d %H:%M:%S') if account.suspended_until else "무기한 정지"
                })
            return Response({"success": True, "suspended_accounts": result}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e), "success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

