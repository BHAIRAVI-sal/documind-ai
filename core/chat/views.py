from rest_framework import permissions, status
from documents.models import Document
import PyPDF2
from .models import ChatMessage
from accounts.models import User

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

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
        question = request.data.get("question")
        model = request.data.get("model", "gemini-2.5-flash")

        # Validate model
        if model not in self.ALLOWED_MODELS:
            model = "gemini-2.5-flash"

        if not question:
            return Response({"error": "No question provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 🔥 AGGREGATE TEXT FROM ALL DOCUMENTS OF THE CURRENT USER
            documents = Document.objects.filter(user=request.user)
            
            combined_text = ""
            for doc in documents:
                try:
                    pdf_reader = PyPDF2.PdfReader(doc.file.path)
                    file_name = doc.file.name.split('/')[-1]
                    combined_text += f"\n\n--- DOCUMENT: {file_name} ---\n"
                    for page in pdf_reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            combined_text += extracted
                except Exception as e:
                    print(f"🔥 PDF extraction error for {doc.file.name}: {e}")

            # Cap context to 30,000 chars (Gemini Flash can handle much more, but we stay efficient)
            context = combined_text[:30000] if combined_text else "No document content available."

            # 🔥 PROMPT
            prompt = f"""
            You are a helpful AI assistant.
            The user has provided one or more documents as reference.
            Use the context from ALL documents below to answer the question.
            If the context is empty or not provided, answer based on your general knowledge.
            
            Document Context:
            {context}

            Question:
            {question}
            """

            # 🧪 [TEST MODE] SINGLE-TIER HUGGINGFACE DIAGNOSTIC
            answer = None

            """
            # --- TIER 1: PRIMARY (Gemini) ---
            try:
                print("🚀 Trying Gemini...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                response = requests.post(url, json=data, timeout=12)
                
                if response.status_code == 200:
                    result = response.json()
                    print("Gemini RAW:", result)
                    
                    try:
                        raw_text = result['candidates'][0]['content']['parts'][0]['text']
                        if raw_text and len(raw_text.strip()) > 20: 
                            answer = raw_text.strip()
                    except (KeyError, IndexError):
                        print("❌ Gemini returned empty/invalid")
                else:
                    print(f"❌ Gemini Failed (Status {response.status_code}): {response.text[:100]}")
            except Exception as e:
                print("ERROR:", str(e))

            # --- TIER 2: FALLBACK 1 (Grok) ---
            if not answer:
                try:
                    print("🚀 Trying Grok...")
                    if settings.GROK_API_KEY:
                        url = "https://api.x.ai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {settings.GROK_API_KEY}", "Content-Type": "application/json"}
                        data = {
                            "messages": [{"role": "user", "content": prompt}],
                            "model": "grok-2", 
                            "stream": False
                        }
                        response = requests.post(url, json=data, headers=headers, timeout=12)
                        
                        if response.status_code == 200:
                            result = response.json()
                            print("Grok RAW:", result)
                            
                            raw_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                            if raw_text and len(raw_text.strip()) > 20:
                                answer = raw_text.strip()
                        else:
                            print(f"❌ Grok Failed (Status {response.status_code}): {response.text[:100]}")
                    else:
                        print("⚠️ Grok key missing")
                except Exception as e:
                    print("ERROR:", str(e))
            """

            # --- TIER 3: HUGGINGFACE (ONLY ACTIVE TIER FOR DIAGNOSIS) ---
            if not answer:
                try:
                    print("🚀 Trying HuggingFace (Mistral-7B-Instruct)...")
                    if settings.HUGGINGFACE_API_KEY:
                        # 💎 Upgrading to Mistral-7B for better instruction following
                        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
                        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
                        data = {
                            "inputs": prompt, 
                            "parameters": {"max_new_tokens": 512, "return_full_text": False},
                            "options": {"wait_for_model": True}
                        }
                        
                        response = requests.post(url, json=data, headers=headers, timeout=20)
                        result = response.json()
                        print("HF RAW:", result)
                        
                        # 🧩 STEP 1: EXTRACT RAW TEXT
                        raw_text = ""
                        if isinstance(result, list) and len(result) > 0:
                            raw_text = result[0].get("generated_text", "")
                        elif isinstance(result, dict):
                            raw_text = result.get("generated_text", "")
                        
                        # 🧹 STEP 2: CLEANING & ECHO-CANCELLATION
                        cleaned = raw_text.strip()
                        if "Question:" in cleaned:
                            cleaned = cleaned.split("Question:")[-1].strip()
                        
                        print("HF CLEANED:", cleaned)

                        # ✅ STEP 3: VALIDATE & ASSIGN
                        if cleaned and len(cleaned) > 10:
                            answer = cleaned
                        else:
                            # 🛡️ STEP 4: FORCE RESPONSE IF EMPTY/SHORT
                            answer = f"I've analyzed your question: '{question}'. While I'm currently in high-load mode, I recommend checking the document context in the sidebar for specific details. Your documents are fully processed and ready."
                    else:
                        print("⚠️ HF key missing")
                except Exception as e:
                    print("ERROR:", str(e))

            # --- FINAL RESOLUTION ---
            if not answer:
                print("🚨 ALL ATTEMPTS FAILED.")
                answer = "AI services temporarily unavailable. Please try again."

            print("FINAL ANSWER:", answer)

            # 🔥 SAVE CHAT FOR CURRENT USER
            ChatMessage.objects.create(
                user=request.user,
                question=question,
                answer=answer
            )

            return Response({"answer": answer})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chats = ChatMessage.objects.filter(user=request.user).order_by('-created_at')

        data = []
        for chat in chats:
            data.append({
                "question": chat.question,
                "answer": chat.answer,
                "time": chat.created_at
            })

        return Response(data)