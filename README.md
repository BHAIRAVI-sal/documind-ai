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
