User login with a modern and intuitive UI/UX for a seamless experience.
<img width="1919" height="922" alt="image" src="https://github.com/user-attachments/assets/faa7896c-fc90-4bcf-8ca9-cc6815fa7ccd" />

User registration with a clean and modern UI/UX for a smooth onboarding experience.
<img width="1918" height="947" alt="image" src="https://github.com/user-attachments/assets/1bc5d2f6-84b6-458d-a979-84a84e384f18" />

AI-powered document analysis with an interactive chat interface for smarter insights.
<img width="1600" height="774" alt="image" src="https://github.com/user-attachments/assets/e3f1ab18-7669-4ec6-9561-f098ac89c0d3" />

Supports simultaneous upload of multiple PDFs for efficient document processing.
<img width="1919" height="945" alt="image" src="https://github.com/user-attachments/assets/a11bff59-c28f-4e25-8725-baadded666ed" />
<img width="1918" height="924" alt="image" src="https://github.com/user-attachments/assets/a8e24c86-8079-4089-bd67-fbdd514d43fa" />

Generate concise summaries of multiple uploaded PDFs simultaneously for quick insights.
<img width="1919" height="936" alt="image" src="https://github.com/user-attachments/assets/b1da0bfd-9ceb-4d95-9cd1-fcd697e264f9" />

Extract key insights and perform advanced analysis on uploaded documents for deeper understanding.
<img width="1919" height="934" alt="image" src="https://github.com/user-attachments/assets/4199679f-53e0-499e-ad1a-7cb4b9865e7a" />

Allows users to edit AI-generated responses for improved accuracy and customization.
<img width="1918" height="942" alt="image" src="https://github.com/user-attachments/assets/2afb9a27-eef5-4fae-a25c-9b876069a690" />

Enables zoomed view of responses for enhanced readability and detailed analysis.
<img width="1919" height="925" alt="image" src="https://github.com/user-attachments/assets/10b45c37-5bb7-4eb9-9463-ebe705b64090" />

Export analyzed content to Word format for easy sharing and documentation.
<img width="1919" height="912" alt="image" src="https://github.com/user-attachments/assets/db0d38a7-f2e1-4e8d-a0e4-533735bc7fd3" />

Allows users to quickly copy generated responses for easy reuse and sharing.
<img width="1919" height="944" alt="image" src="https://github.com/user-attachments/assets/c2d43cd9-3ee2-48db-ad87-09d201981f2e" />

Enables users to provide feedback on AI-generated responses
<img width="1919" height="922" alt="image" src="https://github.com/user-attachments/assets/b22e5e2d-ad79-4dfd-8198-6691342aedce" />

Supports negative feedback on responses
<img width="1919" height="953" alt="image" src="https://github.com/user-attachments/assets/81929c90-dc97-4da7-b8a8-4cffee522eed" />

Supports both light and dark modes for an enhanced and customizable user experience.
<img width="1919" height="931" alt="image" src="https://github.com/user-attachments/assets/52e0d9fe-4d9d-4133-80e8-a943752956fe" />

Allows users to save chats with options to rename, pin, and delete for better conversation management.
<img width="1919" height="947" alt="image" src="https://github.com/user-attachments/assets/b4360f66-9bd9-42b6-bff4-3c3fc60f5df9" />

Allows users to upload documents directly from the search bar for quick and seamless access.
<img width="1919" height="933" alt="image" src="https://github.com/user-attachments/assets/f0c20f2f-fa51-4fb0-ae90-41e406cb7879" />

Provides a secure logout option to safely end user sessions.
<img width="1919" height="892" alt="image" src="https://github.com/user-attachments/assets/9851ecb5-9727-4f68-9413-e4f2743f894e" />

# InsightLens - DocuMind AI

InsightLens is a premium AI-powered document analysis platform that transforms how you interact with your PDFs. It uses a sophisticated multi-AI pipeline to analyze complex documents and provides deep insights through an intuitive, theme-aware chat interface.

![Main Dashboard Placeholder](screenshots/dashboard.png)
*InsightLens Dashboard - Your central hub for document intelligence*

---

## 🚀 Key Features

- **Multi-AI Pipeline**: Leverage the power of **Gemini**, **Grok**, and **HuggingFace** models for robust, prioritized analysis.
- **Isolated User Context**: Each user has their own secure account and private chat history.
- **Smart Context Awareness**: Upload multiple PDFs and chat with them in a single session; the AI understands document relationships.
- **Premium UI/UX**: A high-density, investor-grade interface with smooth transitions, theme toggling, and interactive feedback.
- **Feature-Rich Toolbar**: Summarize documents, extract key insights, and perform advanced analysis with one click.

---

## 📸 Screenshots

To populate your README with visuals, place your screenshots in a `/screenshots/` directory at the root.

### 🔐 Authentication
![Login Page Placeholder](screenshots/login.png)
*Secure, modern authentication flow for multi-user isolation*

### 📂 Document Management
![Upload Flow Placeholder](screenshots/upload.png)
*Seamless PDF selection, preview, and upload controls*

### 💬 Deep Analysis
![Chat Interaction Placeholder](screenshots/chat.png)
*Context-aware conversations with document-driven responses*

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework, PostgreSQL/SQLite, PyPDF2.
- **Frontend**: React.js, Vanilla CSS (Premium Design System), React Router.
- **AI Integration**: Google Gemini API, x.ai (Grok) API, HuggingFace Inference API.
- **Authentication**: JWT (JSON Web Tokens) with `djangorestframework-simplejwt`.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 16+
- API Keys for Gemini, Grok, and/or HuggingFace.

### 2. Backend Setup
```bash
cd core
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies (ensure django-rest-framework-simplejwt is included)
pip install django djangorestframework PyPDF2 requests django-cors-headers djangorestframework-simplejwt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install

# Start the development server
npm start
```

### 4. Environment Variables
Create a `.env` file in the root directory:
```env
# Backend API Keys
GEMINI_API_KEY=your_gemini_key
GROK_API_KEY=your_grok_key
HUGGINGFACE_API_KEY=your_hf_key

# Database/Secret Keys
SECRET_KEY=your_django_secret_key
DEBUG=True
```

---

## 🔒 Security
- **Data Isolation**: Each user's documents and chat history are linked to their unique ID in the database and partitioned in `localStorage`.
- **JWT Authentication**: Secure token-based access for all API endpoints.

---

## 🤝 Contributing
Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

Developed with ❤️ as part of the DocuMind AI Project.
