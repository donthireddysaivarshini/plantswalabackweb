import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class ContactEmailView(APIView):
    """
    Enquiry receiver endpoint.
    Primary customer contact flow is redirected directly to WhatsApp from the frontend.
    This view remains as a safe fallback logger without SMTP dependency.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        name = data.get('name', '')
        phone = data.get('phone', '')
        email = data.get('email', '')
        issue_type = data.get('issue_type', 'Bulk Inquiry')
        message = data.get('message', '')

        logger.info(
            "Customer Enquiry Received: %s (%s, %s) - Type: %s | Message: %s",
            name, phone, email, issue_type, message
        )
        return Response(
            {"detail": "Inquiry received successfully. Enquiries are also routed to WhatsApp."},
            status=status.HTTP_200_OK
        )