from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .chat_core import make_chain
from .chat_core import make_chain, redis_client

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        if not message:
            return Response({"detail": "message field is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        session_id = str(request.user.id)         
        chain = make_chain(session_id)
        answer = chain.predict(input=message)
        return Response({"answer": answer})
    

# Add this new view
class DeleteChatHistoryAPIView(APIView):
    """
    Deletes all conversation history for the authenticated user from Redis
    by scanning for and deleting all matching keys.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """
        Handles the DELETE request to clear the user's chat history.
        """
        try:
            session_id = str(request.user.id)
            
            # CORRECTED: Define the pattern to match all keys for the user's session.
            # Your Redis data shows keys like 'chat:1:01JZ03QAD9WYV1E28DWN72PW2M'
            pattern = f"chat:{session_id}:*"
            
            # Use scan_iter to find all keys matching the pattern without blocking the server.
            keys_to_delete = [key for key in redis_client.scan_iter(match=pattern)]
            
            if keys_to_delete:
                # If keys are found, delete them all in a single operation.
                redis_client.delete(*keys_to_delete)
                print(f"Deleted {len(keys_to_delete)} keys for pattern '{pattern}' for user {session_id}")
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                # This is the message you were seeing.
                print(f"No Redis keys found matching pattern '{pattern}' for user {session_id}. Nothing to delete.")
                return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            print(f"Error deleting chat history for user {request.user.id}: {e}")
            return Response(
                {"detail": "An error occurred while trying to delete the chat history."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )