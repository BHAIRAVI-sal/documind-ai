from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from .serializers import DocumentSerializer
from accounts.models import User
import PyPDF2


class UploadDocumentView(APIView):
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided"}, status=400)

        user = User.objects.first()

        # Save document
        document = Document.objects.create(
            user=user,
            file=file
        )

        # 🔥 READ PDF TEXT
        pdf_reader = PyPDF2.PdfReader(document.file.path)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text()

        return Response({
            "message": "File uploaded successfully",
            "extracted_text": text[:1000]  # first 1000 chars
        }, status=status.HTTP_201_CREATED)