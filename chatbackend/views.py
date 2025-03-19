from typing import Optional, Dict, Any
from django.http import JsonResponse #type: ignore
from rest_framework import status #type: ignore
from rest_framework.decorators import api_view #type: ignore
from rest_framework.request import Request
from rest_framework.response import Response
from main import ChatModelPortfolio
from logger import logger
# Initialize chat backend with error handling
try:
    chat_backend = ChatModelPortfolio()
except Exception as e:
    logger.error(f"Failed to initialize ChatModelPortfolio: {str(e)}")
    chat_backend = None

def chat(request: Request)-> JsonResponse:
    """
    Health check endpoint to verify chatbot availability.

    Args:
        request: Django HTTP request object

    Returns:
        JsonResponse: Status message indicating chatbot readiness
    """
    try:
            if chat_backend is None:
                logger.warning("Chat backend is not initialized")
                return JsonResponse(
                    {"message": "Chatbot is not ready"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            return JsonResponse(
                {"message": "Chatbot is ready"},
                status=status.HTTP_200_OK
            )
    except Exception as e:
        logger.error(f"Error in chat health check: {str(e)}")
        return JsonResponse(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST'])
def chat_worker(request: Request) -> Response:
    """
    Process chat messages and return responses.

    Args:
        request: Django REST framework request object containing message and optional session_id

    Returns:
        Response: JSON response with message and session_id or error details
    """
    try:
        if request.method != 'POST':
            logger.warning(f"Invalid method: {request.method}")
            return Response(
                {"error": "Method not allowed"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        if chat_backend is None:
            logger.error("Chat backend not available")
            return Response(
                {"error": "Chat service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        data: Dict[str, Any] = request.data
        message: Optional[str] = data.get('message')
        session_id: str = data.get('session_id') or chat_backend.generate_session_id()

        # Input validation
        if not isinstance(message, str) or not message.strip():
            logger.warning("Invalid or empty message received")
            return Response(
                {"error": "Message is required and must be a non-empty string"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(session_id, str) or not session_id.strip():
            logger.warning("Invalid session_id generated")
            return Response(
                {"error": "Invalid session ID"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Process chat message
        try:
            response = chat_backend.ChatHandler(message, session_id)
            logger.info(f"Processed message for session {session_id}")
            
            return Response(
                {
                    "message": response,
                    "session_id": session_id
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return Response(
                {"error": "Failed to process message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Unexpected error in chat_worker: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )