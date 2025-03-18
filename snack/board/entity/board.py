from django.db import models
from django.utils.timezone import now, localtime
from account_profile.entity.account_profile import AccountProfile
import pytz

class Board(models.Model):
    STATUS_CHOICES = [
        ('ongoing', '모집 진행중'),
        ('closed', '모집 종료')
    ]

    id = models.AutoField(primary_key=True)  # 게시글 ID
    title = models.CharField(max_length=255)  # 게시글 제목
    content = models.TextField()  # 게시글 내용
    image_url = models.URLField(null=True, blank=True)  # 이미지 업로드
    author = models.ForeignKey(AccountProfile, on_delete=models.CASCADE)  # AccountProfile 참조
    created_at = models.DateTimeField(auto_now_add=True)  # 작성 시간
    end_time = models.DateTimeField()  # 모집 종료 시간
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')  # 상태

    class Meta:
        db_table = 'board'
        app_label = 'board'

    def getId(self):
        return self.id

    def getTitle(self):
        return self.title

    def getContent(self):
        return self.content

    def getAuthorNickname(self):
        return self.author.account_nickname if self.author else "알 수 없음"

    def getCreatedAt(self):
        """작성 시간을 한국 시간으로 변환"""
        return localtime(self.created_at).strftime('%Y-%m-%d %H:%M:%S')

    def getEndTime(self):
        """종료 시간을 한국 시간으로 변환"""
        return localtime(self.end_time).strftime('%Y-%m-%d %H:%M:%S')

    def getImageUrl(self):
        return self.image_url if self.image_url else None
    
    def save(self, *args, **kwargs):
        """ 상태 업데이트 로직 """
        kst = pytz.timezone('Asia/Seoul')
        if self.end_time and self.end_time.astimezone(kst) < now().astimezone(kst):
            self.status = 'closed'
        super().save(*args, **kwargs)
