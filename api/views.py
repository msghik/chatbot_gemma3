from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from .models import ChatSession
from .serializers import ChatSessionSerializer
from .chat_core import make_chain, redis_client

# --- View for Managing Chat Sessions (List and Create) ---
class ChatSessionListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all chat sessions for a user or create a new one.
    GET: Returns a list of the user's chat sessions.
    POST: Creates a new chat session for the user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        """
        THIS IS THE CRITICAL PART.
        It filters the results to only include sessions owned by the
        user making the request.
        """
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        This correctly assigns the user when a new session is created.
        """
        serializer.save(user=self.request.user)



# --- View for Handling a specific Chat Session (Send Message, Delete) ---
class ChatSessionDetailAPIView(APIView):
    """
    API view to interact with a specific chat session.
    POST: Send a new message to this chat session.
    DELETE: Delete this chat session and its history from Redis.
    """
    permission_classes = [IsAuthenticated]

    def get_chat_session(self, user, session_id):
        """Helper to get and validate the chat session."""
        try:
            return ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            raise NotFound("Chat session not found.")

    def post(self, request, session_id, *args, **kwargs):
        """
        Handles sending a new message to a specific chat session.
        """
        chat_session = self.get_chat_session(request.user, session_id)
        
        message = request.data.get("message")
        if not message:
            return Response({"detail": "message field is required"}, status=status.HTTP_400_BAD_REQUEST)

        # IMPORTANT: Create a unique session_id for LangChain/Redis
        langchain_session_id = f"user_{request.user.id}_chat_{chat_session.id}"
        
        chain = make_chain(langchain_session_id)
        answer = chain.predict(input=message)
        
        return Response({"answer": answer})

    def delete(self, request, session_id, *args, **kwargs):
        """
        Deletes a chat session from the database and its history from Redis.
        """
        chat_session = self.get_chat_session(request.user, session_id)

        # 1. Delete the history from Redis
        langchain_session_id = f"user_{request.user.id}_chat_{chat_session.id}"
        pattern = f"chat:{langchain_session_id}:*"
        keys_to_delete = [key for key in redis_client.scan_iter(match=pattern)]
        
        if keys_to_delete:
            redis_client.delete(*keys_to_delete)
            print(f"Deleted {len(keys_to_delete)} Redis keys for session {chat_session.id}")
        
        # 2. Delete the session from the SQL database
        chat_session.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)