from django.urls import path
from rest_framework.routers import DefaultRouter
from board.controller.board_controller import BoardController

# DRF Router 설정
router = DefaultRouter()
router.register(r'board', BoardController, basename='board')

urlpatterns = [
    path('board/create/', BoardController.as_view({'post': 'createBoard'}), name='create-board'),
    path('board/<int:board_id>/', BoardController.as_view({'get': 'getBoard'}), name='get-board'),
    path('board/all/', BoardController.as_view({'get': 'getAllBoards'}), name='get-all-boards'),
    path('board/author/<int:author_id>/', BoardController.as_view({'get': 'getBoardsByAuthor'}), name='get-boards-by-author'),
    path('board/end-time-range/<int:start_hour>/<int:end_hour>/', BoardController.as_view({'get': 'getBoardsByEndTimeRange'}), name='get-boards-by-end-time'),
    path('board/update/<int:board_id>/', BoardController.as_view({'put': 'updateBoard'}), name='update-board'),
    path('board/delete/<int:board_id>/', BoardController.as_view({'delete': 'deleteBoard'}), name='delete-board'),
]

# DRF router의 URL을 포함
urlpatterns += router.urls
