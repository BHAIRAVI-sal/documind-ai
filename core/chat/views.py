import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from documents.models import Document
import PyPDF2
from .models import ChatMessage
from accounts.models import User


class ChatWithDocumentView(APIView):
    # Free Gemini Flash models whitelist
    ALLOWED_MODELS = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
    ]

    def post(self, request):
        question = request.data.get("question")
        model = request.data.get("model", "gemini-2.5-flash")

        # Validate model
        if model not in self.ALLOWED_MODELS:
            model = "gemini-2.5-flash"

        if not question:
            return Response({"error": "No question provided"}, status=400)

        try:
            # 🔥 GET LATEST DOCUMENT
            document = Document.objects.last()

            text = ""
            if document:
                pdf_reader = PyPDF2.PdfReader(document.file.path)

                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted

            context = text[:15000]

            # 🔥 PROMPT
            prompt = f"""
            You are a helpful AI assistant.

            Use the document below as reference if relevant.
            If the answer is not in the document, answer normally like ChatGPT.

            Document:
            {context}

            Question:
            {question}
            """

            # 🔥 API CALL (SECURE) - uses selected model
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"

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

            print("🔥 Gemini API status:", response.status_code)
            print("🔥 Gemini API response:", str(result)[:300])

            # 🔥 HANDLE API ERRORS
            if response.status_code == 429:
                return Response({
                    "answer": "⚠️ API rate limit reached. Please wait a moment and try again."
                })

            if response.status_code != 200:
                return Response({
                    "answer": f"⚠️ API error ({response.status_code}). Please check your Gemini API key."
                })

            if "candidates" not in result:
                return Response({
                    "answer": "⚠️ No response from AI. The API returned an unexpected format."
                })

            answer = result['candidates'][0]['content']['parts'][0]['text']

            # 🔥 SAVE CHAT
            user = User.objects.first()

            ChatMessage.objects.create(
                user=user,
                question=question,
                answer=answer
            )

            return Response({"answer": answer})

        except Exception as e:
            return Response({"error": str(e)}, status=500)


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