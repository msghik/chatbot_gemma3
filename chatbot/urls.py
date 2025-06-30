from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.views import (
    ChatSessionListCreateAPIView, 
    ChatSessionDetailAPIView
)
from api.auth_views import TokenVerifyWithUserIdView 

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/",   TokenVerifyWithUserIdView.as_view(), name="token_verify"),

    # === NEW CHAT ENDPOINTS FOR MULTIPLE SESSIONS ===
    
    # This URL is for listing all of a user's chat sessions or creating a new one.
    # GET /api/chats/ -> Lists all chat sessions for the authenticated user.
    # POST /api/chats/ -> Creates a new, empty chat session for the user.
    path("api/chats/", ChatSessionListCreateAPIView.as_view(), name="chat_session_list_create"),

    # This URL is for interacting with one specific chat session by its ID.
    # POST /api/chats/<int:session_id>/ -> Sends a message to this specific chat.
    # DELETE /api/chats/<int:session_id>/ -> Deletes this specific chat and its history.
    path("api/chats/<int:session_id>/", ChatSessionDetailAPIView.as_view(), name="chat_session_detail"),


    # === OLD ENDPOINTS (REMOVED) ===
    # The two lines below are now replaced by the new, more flexible system above.
    # path("api/chat/", ChatAPIView.as_view(), name="chat"),
    # path("api/chat/delete/", DeleteChatHistoryAPIView.as_view(), name='delete_chat_history'),
]