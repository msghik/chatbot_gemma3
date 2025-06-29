from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .chat_core import make_chain

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        if not message:
            return Response({"detail": "message field is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        session_id = str(request.user.id)           # یا هر شناسه دلخواه
        chain = make_chain(session_id)
        answer = chain.predict(input=message)
        return Response({"answer": answer})
    

