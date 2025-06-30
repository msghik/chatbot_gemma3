from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from api.views import ChatAPIView, DeleteChatHistoryAPIView
from api.auth_views import TokenVerifyWithUserIdView 

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/",   TokenVerifyWithUserIdView.as_view(), name="token_verify"),

    # chat endpoint
    path("api/chat/", ChatAPIView.as_view(), name="chat"),
    path("api/chat/delete/", DeleteChatHistoryAPIView.as_view(), name='delete_chat_history'),

]