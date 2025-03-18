from django.http import JsonResponse
from rest_framework import viewsets, status
from board.service.board_service_impl import BoardServiceImpl
from account_profile.entity.account_profile import AccountProfile
from django.core.exceptions import ObjectDoesNotExist

class BoardController(viewsets.ViewSet):
    __boardService = BoardServiceImpl.getInstance()

    def createBoard(self, request):
        """새로운 게시글을 생성하는 엔드포인트"""
        postRequest = request.data
        title = postRequest.get("title")
        content = postRequest.get("content")
        author_id = postRequest.get("author_id")
        image = request.FILES.get("image")  # 이미지 파일 (선택적)
        end_time = postRequest.get("end_time")  # 종료 시간

        if not title or not content or not author_id or not end_time:
            return JsonResponse({"error": "title, content, author_id, end_time이 필요합니다.", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            author = AccountProfile.objects.get(account__id=author_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "작성자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        board = self.__boardService.createBoard(title, content, author, image, end_time)

        return JsonResponse({
            "success": True,
            "board_id": board.id,
            "title": board.title,
            "author_nickname": board.getAuthorNickname()
            "image_url" : board.getImageUrl()
        }, status=status.HTTP_201_CREATED)

    def getBoard(self, request, board_id):
        """특정 게시글 조회"""
        board = self.__boardService.findBoardById(board_id)
        if not board:
            return JsonResponse({"error": "게시글을 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({
            "board_id": board.id,
            "title": board.title,
            "content": board.content,
            "author_nickname": board.getAuthorNickname(),
            "created_at": board.getCreatedAt(),
            "end_time": board.getEndTime(),
            "status": board.status,
            "success": True
        }, status=status.HTTP_200_OK)

    def getAllBoards(self, request):
        """모든 게시글 조회"""
        boards = self.__boardService.findAllBoards()
        board_list = [
            {
                "board_id": board.id,
                "title": board.title,
                "author_nickname": board.getAuthorNickname(),
                "created_at": board.getCreatedAt(),
                "end_time": board.getEndTime(),
                "status": board.status
            }
            for board in boards
        ]

        return JsonResponse({"success": True, "boards": board_list}, status=status.HTTP_200_OK)

    def getBoardsByAuthor(self, request, author_id):
        """특정 작성자의 게시글 조회"""
        try:
            author = AccountProfile.objects.get(account__id=author_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "작성자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        boards = self.__boardService.findBoardsByAuthor(author)
        board_list = [
            {
                "board_id": board.id,
                "title": board.title,
                "created_at": board.getCreatedAt(),
                "end_time": board.getEndTime(),
                "status": board.status
            }
            for board in boards
        ]

        return JsonResponse({"success": True, "boards": board_list}, status=status.HTTP_200_OK)

    def getBoardsByEndTimeRange(self, request, start_hour, end_hour):
        """특정 시간대 (예: 07:00~10:00) 내 모집 종료되는 게시글 조회"""
        boards = self.__boardService.findBoardsByEndTimeRange(start_hour, end_hour)
        board_list = [
            {
                "board_id": board.id,
                "title": board.title,
                "created_at": board.getCreatedAt(),
                "end_time": board.getEndTime(),
                "status": board.status
            }
            for board in boards
        ]

        return JsonResponse({"success": True, "boards": board_list}, status=status.HTTP_200_OK)

    def updateBoard(self, request, board_id):
        """게시글 수정"""
        postRequest = request.data
        title = postRequest.get("title")
        content = postRequest.get("content")
        image = request.FILES.get("image")
        end_time = postRequest.get("end_time")

        updated_board = self.__boardService.updateBoard(board_id, title, content, image, end_time)
        if not updated_board:
            return JsonResponse({"error": "게시글을 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({
            "success": True,
            "message": "게시글이 수정되었습니다.",
            "board_id": updated_board.id,
            "title": updated_board.title
        }, status=status.HTTP_200_OK)

    def deleteBoard(self, request, board_id):
        """게시글 삭제"""
        user_id = request.data.get("user_id")

        if not user_id:
            return JsonResponse({"error": "user_id가 필요합니다.", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = AccountProfile.objects.get(account__id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "사용자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        deleted = self.__boardService.deleteBoard(board_id, user)
        if not deleted:
            return JsonResponse({"error": "삭제 권한이 없습니다.", "success": False}, status=status.HTTP_403_FORBIDDEN)

        return JsonResponse({"success": True, "message": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
