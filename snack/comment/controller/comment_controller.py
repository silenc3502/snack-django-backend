from django.http import JsonResponse
from rest_framework import viewsets, status
from comment.service.comment_service_impl import CommentServiceImpl
from board.entity.board import Board
from account_profile.entity.account_profile import AccountProfile
from comment.entity.comment import Comment
from django.core.exceptions import ObjectDoesNotExist


class CommentController(viewsets.ViewSet):
    __commentService = CommentServiceImpl.getInstance()

    def createComment(self, request):
        """새로운 댓글 생성"""
        postRequest = request.data
        board_id = postRequest.get("board_id")
        author_id = postRequest.get("author_id")
        content = postRequest.get("content")

        if not board_id or not author_id or not content:
            return JsonResponse({"error": "board_id, author_id, content가 필요합니다.", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            board = Board.objects.get(id=board_id)
            author = AccountProfile.objects.get(account__id=author_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "게시글 또는 작성자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        comment = self.__commentService.createComment(board, author, content)

        return JsonResponse({
            "success": True,
            "comment_id": comment.id,
            "content": comment.content,
            "author_nickname": comment.getAuthorNickname()
        }, status=status.HTTP_201_CREATED)

    def createReply(self, request):
        """대댓글 생성"""
        postRequest = request.data
        board_id = postRequest.get("board_id")
        author_id = postRequest.get("author_id")
        content = postRequest.get("content")
        parent_id = postRequest.get("parent_id")

        if not board_id or not author_id or not content or not parent_id:
            return JsonResponse({"error": "board_id, author_id, content, parent_id가 필요합니다.", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            board = Board.objects.get(id=board_id)
            author = AccountProfile.objects.get(account__id=author_id)
            parent = Comment.objects.get(id=parent_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "게시글, 작성자 또는 부모 댓글을 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        reply = self.__commentService.createComment(board, author, content, parent)

        return JsonResponse({
            "success": True,
            "comment_id": reply.id,
            "content": reply.content,
            "author_nickname": reply.getAuthorNickname(),
            "parent_id": reply.parent.id if reply.parent else None,
        }, status=status.HTTP_201_CREATED)

    def getComment(self, request, comment_id):
        """특정 댓글 조회"""
        comment = self.__commentService.findCommentById(comment_id)
        if not comment:
            return JsonResponse({"error": "댓글을 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({
            "comment_id": comment.id,
            "board_id": comment.getBoardId(),
            "content": comment.content,
            "author_nickname": comment.getAuthorNickname(),
            "created_at": comment.getCreatedAt(),
            "success": True
        }, status=status.HTTP_200_OK)

    def getAllCommentsByBoard(self, request, board_id):
        """게시글의 모든 댓글 조회"""
        try:
            board = Board.objects.get(id=board_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "게시글을 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(board=board).select_related("author", "parent").order_by("id")
        comment_list = [
            {
                "comment_id": comment.id,
                "content": comment.content,
                "author_nickname": comment.getAuthorNickname(),
                "created_at": comment.getCreatedAt(),
                "author_account_id": comment.author.account.id if comment.author and comment.author.account else None,
                "parent_id": comment.parent.id if comment.parent else None,
            }
            for comment in comments
        ]

        return JsonResponse({"success": True, "comments": comment_list}, status=status.HTTP_200_OK)

    def getAllCommentsByAuthor(self, request, author_id):
        """작성자의 모든 댓글 조회"""
        try:
            author = AccountProfile.objects.get(account__id=author_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "작성자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        comments = self.__commentService.findAllCommentsByAuthor(author)
        comment_list = [
            {
                "comment_id": comment.id,
                "content": comment.content,
                "board_id": comment.getBoardId(),
                "created_at": comment.getCreatedAt()
            }
            for comment in comments
        ]

        return JsonResponse({"success": True, "comments": comment_list}, status=status.HTTP_200_OK)

    def deleteComment(self, request, comment_id):
        """댓글 삭제"""
        user_id = request.data.get("user_id")
        user_token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not user_id:
            return JsonResponse({"error": "user_id가 필요합니다.", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = AccountProfile.objects.get(account__id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "사용자를 찾을 수 없습니다.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        deleted, status_code, message = self.__commentService.deleteComment(comment_id, user_token)
        return JsonResponse({"success": deleted, "message": message}, status=status_code)
