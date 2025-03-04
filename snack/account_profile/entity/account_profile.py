from django.db import models
from account.entity.account import Account
from django.utils.timezone import now
from datetime import date

class AccountProfile(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)  # FK + PK
    account_name = models.CharField(max_length=100)  # 사용자 이름 (수정 불가)
    account_nickname = models.CharField(max_length=100)  # 닉네임 (수정 가능)
    phone_num = models.CharField(max_length=20, null=True, blank=True)  # 핸드폰 번호 (수정 가능)
    account_add = models.CharField(max_length=255, null=True, blank=True)  # 주소 (수정 가능)
    account_sex = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('Other', 'Other')],
        null=True,
        blank=True
    )  # 성별 (수정 불가)
    account_birth = models.DateField(null=True, blank=True)  # 생년월일 (수정 불가)
    account_pay = models.JSONField(null=True, blank=True)  # 결제 정보 (수정 가능)
    account_sub = models.BooleanField(default=False)  # 구독 여부 (수정 가능)
    account_age = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'account_profile'
        app_label = 'account_profile'

    def __str__(self):
        return f"{self.account_nickname} - 가입일: {self.account.account_register.strftime('%Y-%m-%d')}"

    def get_age(self):
        """생년월일을 기준으로 현재 나이를 계산"""
        if self.account_birth:
            today = date.today()
            return today.year - self.account_birth.year - ((today.month, today.day) < (self.account_birth.month, self.account_birth.day))
        return None
    
    def save(self, *args, **kwargs):
        """저장하기 전에 자동으로 account_age 값을 업데이트"""
        self.account_age = self.get_age()  # 나이 계산 후 저장
        super().save(*args, **kwargs)