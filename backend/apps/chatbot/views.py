from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .serializers import ChatRequestSerializer
from .services.chat_service import ChatService

class ChatAPIView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            session_id = serializer.validated_data.get('session_id')
            message = serializer.validated_data.get('message')
            metadata = serializer.validated_data.get('metadata') # passed to chat_service if needed in future

            chat_service = ChatService()
            result = chat_service.process_message(session_id, message)

            return Response(result, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HealthAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
