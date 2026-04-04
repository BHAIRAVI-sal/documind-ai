from rest_framework import status, permissions
from .models import Document
from .serializers import DocumentSerializer
import PyPDF2

from rest_framework.views import APIView
from rest_framework.response import Response

class UploadDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        files = request.FILES.getlist('file')

        if not files:
            return Response({"error": "No file(s) provided"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_documents = []
        total_text_extracted = ""

        # 🔥 Iterate through all uploaded files
        for file in files:
            # Save document for the logged-in user
            document = Document.objects.create(
                user=request.user,
                file=file
            )
            
            # 🔥 READ PDF TEXT (Robust extraction for each file)
            try:
                pdf_reader = PyPDF2.PdfReader(document.file.path)
                file_text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        file_text += extracted
                
                # Combine text from all files for the preview response
                total_text_extracted += f"\n--- {file.name} ---\n{file_text}"
                uploaded_documents.append({
                    "id": document.id,
                    "name": file.name
                })
            except Exception as e:
                print(f"🔥 Error extracting text from {file.name}: {e}")

        return Response({
            "message": f"{len(files)} file(s) uploaded successfully",
            "uploaded_files": uploaded_documents,
            "extracted_text_preview": total_text_extracted[:2000] if total_text_extracted else "No text found."
        }, status=status.HTTP_201_CREATED)