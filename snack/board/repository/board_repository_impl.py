from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from uuid import uuid4
from board.entity.board import Board
from board.repository.board_repository import BoardRepository
from account_profile.entity.account_profile import AccountProfile
from utility.s3_client import S3Client
from restaurants.entity.restaurants import Restaurant
from django.db.models import Count

class BoardRepositoryImpl(BoardRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__s3_client = S3Client.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance


    def save(self, board: Board):
        """새로운 게시글을 저장한다."""
        board.save()
        return board

    def findById(self, board_id: int):
        """ID로 게시글을 찾는다."""
        try:
            return Board.objects.get(id=board_id)
        except ObjectDoesNotExist:
            return None

    def findAll(self):
        return Board.objects.select_related("author__account", "restaurant").all()

    def searchBoards(self, keyword: str):
        from account_profile.entity.account_profile import AccountProfile
        from django.db.models import Q

        # 1. 제목으로 검색
        title_matched = Board.objects.filter(title__icontains=keyword)

        # 2. 식당 주소로 검색
        address_matched = Board.objects.filter(restaurant__address__icontains=keyword)

        # 3. 작성자 닉네임으로 검색
        matched_authors = AccountProfile.objects.filter(account_nickname__icontains=keyword)
        author_matched = Board.objects.filter(author__in=matched_authors)

        # 4. 전체 결과 합치기
        return title_matched | address_matched | author_matched

    def findByAuthor(self, author: AccountProfile):
        """작성자의 게시글을 조회한다."""
        return list(Board.objects.filter(author=author))

    def findByEndTimeRange(self, start_hour: int, end_hour: int):
        """특정 시간 범위에 모집 종료되는 게시글을 조회한다."""
        return list(Board.objects.filter(
            end_time__hour__gte=start_hour,
            end_time__hour__lte=end_hour
        ))

    def delete(self, board_id: int):
        """게시글을 삭제한다."""
        board = self.findById(board_id)
        if board:
            board.delete()
            return True
        return False
    
    def countBoardsByRestaurant(self):
        """식당별 게시글 수 반환"""
        return (
            Board.objects.filter(status='ongoing')
            .values('restaurant_id')
            .annotate(board_count=Count('id'))
            .order_by('restaurant_id')
        )

