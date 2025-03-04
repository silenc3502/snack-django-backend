from django.urls import path, include
from rest_framework.routers import DefaultRouter

from naver_authentication.controller.naver_oauth_controller import naverOauthController

router = DefaultRouter()
router.register(r"naver-oauth", naverOauthController, basename='naver-oauth')

urlpatterns = [
    path('', include(router.urls)),
    path('request-login-url',
         naverOauthController.as_view({ 'get': 'requestnaverOauthLink' }),
         name='naver Oauth 링크 요청'),
    path('redirect-access-token',
         naverOauthController.as_view({ 'post': 'requestAccessToken' }),
         name='naver Access Token 요청'),
     path('request-user-token',
         naverOauthController.as_view({ 'post': 'requestUserToken' }),
         name='User Token 요청'),
]