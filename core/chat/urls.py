from django.urls import path
from .views import ChatWithDocumentView, ChatHistoryView

urlpatterns = [
    path('ask/', ChatWithDocumentView.as_view()),
    path('history/', ChatHistoryView.as_view()),
]