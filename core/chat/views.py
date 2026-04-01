import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from documents.models import Document
import PyPDF2
from .models import ChatMessage
from accounts.models import User


class ChatWithDocumentView(APIView):
    def post(self, request):
        question = request.data.get("question")

        if not question:
            return Response({"error": "No question provided"}, status=400)

        try:
            # 🔥 GET LATEST DOCUMENT
            document = Document.objects.last()

            text = ""
            if document:
                pdf_reader = PyPDF2.PdfReader(document.file.path)

                for page in pdf_reader.pages:
                    text += page.extract_text()

            context = text[:15000]

            # 🔥 HYBRID PROMPT
            prompt = f"""
            You are a helpful AI assistant.

            Use the document below as reference if relevant.
            If the answer is not in the document, answer normally like ChatGPT.

            Document:
            {context}

            Question:
            {question}
            """

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"

            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }

            response = requests.post(url, json=data)
            result = response.json()

            if "candidates" not in result:
                return Response({
                    "error": "API issue",
                    "full_response": result
                })

            answer = result['candidates'][0]['content']['parts'][0]['text']

            # 🔥 SAVE CHAT HISTORY
            user = User.objects.first()

            ChatMessage.objects.create(
                user=user,
                question=question,
                answer=answer
            )

            return Response({
                "answer": answer
            })

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=500)


class ChatHistoryView(APIView):
    def get(self, request):
        user = User.objects.first()

        chats = ChatMessage.objects.filter(user=user).order_by('-created_at')

        data = []
        for chat in chats:
            data.append({
                "question": chat.question,
                "answer": chat.answer,
                "time": chat.created_at
            })

        return Response(data)