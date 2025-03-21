from django.db import models
from account.entity.account_role_type import AccountRoleType
from django.utils.timezone import now, localtime
import pytz

class Account(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, unique=True)  # 이메일 (로그인 시 필수)
    role_type = models.ForeignKey(AccountRoleType, on_delete=models.CASCADE)  # 사용자 역할 (관리자, 사용자, 구독자)
    account_register = models.DateTimeField(auto_now_add=True)  # 계정 생성 날짜
    account_used_date = models.DateTimeField(auto_now=True)  # 마지막 로그인 날짜
    account_path = models.CharField(
        max_length=10,
        choices=[('kakao', 'Kakao'), ('naver', 'Naver'), ('google', 'Google'), ('us', 'Us')],
        null=True,
        blank=True
    )  # 가입 경로
    is_active = models.BooleanField(default=True)  # 계정 활성 상태 (Soft Delete)

    class Meta:
        db_table = 'account'
        app_label = 'account'
    
    def getId(self):
        return self.id
    
    def getEmail(self):
        return self.email

    def update_last_used(self):
        """최근 로그인 날짜를 현재 시간으로 갱신"""
        kst = pytz.timezone('Asia/Seoul')
        self.account_used_date = now().astimezone(kst)
        self.save(update_fields=['account_used_date'])

    def get_register_time_kst(self):
        """계정 생성 날짜 한국 시간으로 변환"""
        return localtime(self.account_register).strftime('%Y-%m-%d %H:%M:%S')  