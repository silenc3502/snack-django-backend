from django.urls import path
from rest_framework.routers import DefaultRouter
from comment.controller.comment_controller import CommentController

# DRF Router 설정
router = DefaultRouter()
router.register(r'comment', CommentController, basename='comment')

urlpatterns = [
    path('comment/create/', CommentController.as_view({'post': 'createComment'}), name='create-comment'),
    path('comment/<int:comment_id>/', CommentController.as_view({'get': 'getComment'}), name='get-comment'),
    path('comment/board/<int:board_id>/', CommentController.as_view({'get': 'getAllCommentsByBoard'}), name='get-comments-by-board'),
    path('comment/author/<int:author_id>/', CommentController.as_view({'get': 'getAllCommentsByAuthor'}), name='get-comments-by-author'),
    path('comment/delete/<int:comment_id>/', CommentController.as_view({'delete': 'deleteComment'}), name='delete-comment'),
]

# DRF router의 URL을 포함
urlpatterns += router.urls
