# backend/mails/urls.py
from django.urls import path
from .views import ContactEmailView  # <--- Change this from ContactFormView

urlpatterns = [
    # This will result in the full URL: /api/forms/contact/
    path('contact/', ContactEmailView.as_view(), name='contact_api'),
    path('bulk-order/', ContactEmailView.as_view(), name='bulk_order_api'),
]