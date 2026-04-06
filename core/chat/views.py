from rest_framework import permissions, status
from documents.models import Document
import PyPDF2
from .models import ChatMessage
from accounts.models import User

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatHistorySerializer

class ChatWithDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Free Gemini Flash models whitelist
    ALLOWED_MODELS = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
    ]

    def post(self, request):
        # 1. Safely handle unauthenticated users
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required to perform document analysis."}, status=status.HTTP_401_UNAUTHORIZED)

        question = request.data.get("question")
        model_name = request.data.get("model", "gemini-2.5-flash")

        # Validate model selection
        if model_name not in self.ALLOWED_MODELS:
            model_name = "gemini-2.5-flash"

        if not question:
            return Response({"error": "No question provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Robust Document Content Extraction for the Current User
            documents = Document.objects.filter(user=request.user)
            combined_text = ""
            
            for doc in documents:
                try:
                    if doc.file and hasattr(doc.file, 'path'):
                        pdf_reader = PyPDF2.PdfReader(doc.file.path)
                        file_name = doc.file.name.split('/')[-1]
                        combined_text += f"\n\n--- DOCUMENT: {file_name} ---\n"
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                combined_text += text
                except Exception as extraction_err:
                    print(f"PDF extraction error for {doc.id}: {str(extraction_err)}")

            # Cap context to prevent token overflows (approx 30k chars)
            context = combined_text[:30000] if combined_text else "No document content provided by user."

            prompt = f"""
            You are a helpful senior AI research assistant.
            Use the context from the documents provided below to answer the user's question.
            If the context is insufficient, use your broad internal knowledge while prioritizing document facts.
            
            Document Context:
            {context}

            Question:
            {question}
            """

            answer = None

            # 3. AI Multi-Tier Pipeline - Tier 1: Gemini (Primary)
            gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if gemini_api_key:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    headers = {"Content-Type": "application/json"}
                    
                    response = requests.post(url, json=payload, headers=headers, timeout=15)
                    if response.status_code == 200:
                        res_json = response.json()
                        candidates = res_json.get('candidates', [])
                        if candidates:
                            parts = candidates[0].get('content', {}).get('parts', [])
                            if parts:
                                raw_answer = parts[0].get('text', '').strip()
                                if len(raw_answer) > 5:
                                    answer = raw_answer
                except Exception as e:
                    print(f"Gemini API Exception: {str(e)}")

            # 4. AI Multi-Tier Pipeline - Tier 2: Grok Fallback
            if not answer:
                grok_key = getattr(settings, 'GROK_API_KEY', None)
                if grok_key:
                    try:
                        url = "https://api.x.ai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
                        data = {
                            "messages": [{"role": "user", "content": prompt}],
                            "model": "grok-2",
                            "stream": False
                        }
                        response = requests.post(url, json=data, headers=headers, timeout=15)
                        if response.status_code == 200:
                            res_json = response.json()
                            raw_answer = res_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                            if len(raw_answer) > 5:
                                answer = raw_answer
                    except Exception as e:
                        print(f"Grok API Exception: {str(e)}")

            # 5. AI Multi-Tier Pipeline - Tier 3: HuggingFace Fallback
            if not answer:
                hf_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
                if hf_key:
                    try:
                        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
                        headers = {"Authorization": f"Bearer {hf_key}"}
                        data = {
                            "inputs": prompt,
                            "parameters": {"max_new_tokens": 512, "return_full_text": False},
                            "options": {"wait_for_model": True}
                        }
                        response = requests.post(url, json=data, headers=headers, timeout=20)
                        if response.status_code == 200:
                            res_json = response.json()
                            raw_text = ""
                            if isinstance(res_json, list) and len(res_json) > 0:
                                raw_text = res_json[0].get("generated_text", "")
                            elif isinstance(res_json, dict):
                                raw_text = res_json.get("generated_text", "")
                            
                            cleaned = raw_text.strip()
                            if "Question:" in cleaned:
                                cleaned = cleaned.split("Question:")[-1].strip()
                            if len(cleaned) > 5:
                                answer = cleaned
                    except Exception as e:
                        print(f"HuggingFace API Exception: {str(e)}")

            # 6. Final Stability Handshake - Ensure a response is always returned
            if not answer:
                answer = "I'm currently experiencing high traffic or connectivity issues with my AI processing tiers. Please try your request again in a moment."

            # 7. Safe Object Creation (Final Integrity Safeguard)
            if request.user and request.user.is_authenticated:
                ChatMessage.objects.create(
                    user=request.user,
                    question=question,
                    answer=answer
                )

            return Response({"answer": answer}, status=status.HTTP_200_OK)

        except Exception as global_err:
            print(f"CRITICAL 500 ERROR: {str(global_err)}")
            return Response(
                {"error": "An unexpected server error occurred while analyzing your docs."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            chats = ChatMessage.objects.filter(user=request.user).order_by('-created_at')
            serializer = ChatHistorySerializer(chats, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)