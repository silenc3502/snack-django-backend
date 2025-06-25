from django.apps import AppConfig
from django.db import models
from account_alarm.entity.alarm_type import AlarmType
from board.entity.board import Board
from comment.entity.comment import Comment
from account.entity.account import Account
from account_profile.entity.account_profile import AccountProfile



class AccountAlarm(models.Model):
    id = models.AutoField(primary_key=True)          # alarm_id
    alarm_type = models.CharField(
        max_length=15,
        choices=AlarmType.choices,  # AlarmType에서 정의된 타입 사용
        default=AlarmType.COMMENT
    )
    is_unread = models.BooleanField(default=True)  # 알림 읽음 여부
    alarm_created_at = models.DateTimeField(auto_now_add=True)  # 알림 생성 시간

    board = models.ForeignKey(Board, on_delete=models.CASCADE)  # board_id
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recipient')  # account_id, 알림 수신자
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)  # comment_id

    class Meta:
        db_table = 'account_alarm'
        app_label = 'account_alarm'
        ordering = ['-alarm_created_at'] # 생성된 시간 내림차순 정렬 (최근 알림이 위로)


