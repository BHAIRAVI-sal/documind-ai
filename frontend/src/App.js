import React, { useState, useEffect, useRef } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import "./App.css";

// Import Auth Components
import Login from "./components/auth/Login";
import Signup from "./components/auth/Signup";

const MODELS = [
  { id: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
  { id: "gemini-2.5-flash-lite", label: "Gemini 2.5 Flash Lite" },
  { id: "gemini-2.0-flash", label: "Gemini 2.0 Flash" },
  { id: "gemini-1.5-flash", label: "Gemini 1.5 Flash" },
];

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem("documind_token");
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

// Main Chat Component (Extracted from old App)
function ChatInterface() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem("documind_sessions");
    return saved ? JSON.parse(saved) : [];
  });

  const [activeSessionId, setActiveSessionId] = useState(() => {
    return localStorage.getItem("documind_active_session_id") || "";
  });

  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("gemini-2.5-flash");

  const [menuOpenId, setMenuOpenId] = useState(null);
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [tempTitle, setTempTitle] = useState("");

  const chatBoxRef = useRef(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [sessions, activeSessionId, loading]);

  useEffect(() => {
    localStorage.setItem("documind_sessions", JSON.stringify(sessions));
    if (activeSessionId) {
      localStorage.setItem("documind_active_session_id", activeSessionId);
    }
  }, [sessions, activeSessionId]);

  useEffect(() => {
    const handleClickOutside = () => setMenuOpenId(null);
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  useEffect(() => {
    const syncHistory = async () => {
      try {
        const token = localStorage.getItem("documind_token");
        const res = await fetch("http://127.0.0.1:8000/api/chat/history/", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const backendHistory = await res.json();

        if (sessions.length === 0 && Array.isArray(backendHistory) && backendHistory.length > 0) {
          const legacyMessages = backendHistory.map(item => ([
            { role: "user", text: item.question },
            { role: "ai", text: item.answer }
          ])).flat();

          const legacySession = {
            id: "legacy-" + Date.now(),
            title: backendHistory[0].question.substring(0, 30) + "...",
            messages: legacyMessages,
            isPinned: false
          };

          setSessions([legacySession]);
          setActiveSessionId(legacySession.id);
        } else if (sessions.length === 0) {
          handleNewChat();
        }
      } catch (e) {
        console.error("History sync error:", e);
        if (sessions.length === 0) handleNewChat();
      }
    };
    syncHistory();
  }, []);

  const handleNewChat = () => {
    const newSession = {
      id: crypto.randomUUID(),
      title: "New Conversation",
      messages: [],
      isPinned: false
    };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newSession.id);
    setQuestion("");
  };

  const askAI = async (customQuestion) => {
    if (!activeSessionId) return;
    const token = localStorage.getItem("documind_token");

    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        return { ...s, messages: [...s.messages, { role: "user", text: customQuestion }] };
      }
      return s;
    }));
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat/ask/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ question: customQuestion, model: model }),
      });
      const data = await res.json();
      setLoading(false);
      setSessions(prev => prev.map(s => {
        if (s.id === activeSessionId) {
          const isFirstMessage = s.messages.length === 1;
          const newTitle = isFirstMessage ? customQuestion.substring(0, 35) : s.title;
          return { ...s, title: newTitle, messages: [...s.messages, { role: "ai", text: data.answer }] };
        }
        return s;
      }));
    } catch (error) {
      console.error("Error asking AI:", error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("documind_token");
    localStorage.removeItem("documind_refresh");
    navigate("/login");
  };

  const handleAsk = () => {
    if (!question) return;
    askAI(question);
    setQuestion("");
  };

  const handleUpload = async () => {
    if (!file) return alert("Select file");
    const token = localStorage.getItem("documind_token");
    const formData = new FormData();
    formData.append("file", file);
    try {
      await fetch("http://127.0.0.1:8000/api/documents/upload/", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData,
      });
      alert("PDF Uploaded ✅");
    } catch (error) {
      console.error("Error uploading:", error);
    }
  };

  const toggleMenu = (e, id) => {
    e.stopPropagation();
    setMenuOpenId(menuOpenId === id ? null : id);
  };

  const handlePin = (id) => {
    setSessions(prev => prev.map(s => s.id === id ? { ...s, isPinned: !s.isPinned } : s));
    setMenuOpenId(null);
  };

  const startRename = (id, currentTitle) => {
    setEditingSessionId(id);
    setTempTitle(currentTitle);
    setMenuOpenId(null);
  };

  const saveRename = (e, id) => {
    if (e.key === "Enter") {
      setSessions(prev => prev.map(s => s.id === id ? { ...s, title: tempTitle } : s));
      setEditingSessionId(null);
    }
    if (e.key === "Escape") setEditingSessionId(null);
  };

  const handleDelete = (e, id) => {
    e.stopPropagation();
    const newSessions = sessions.filter(s => s.id !== id);
    setSessions(newSessions);
    if (activeSessionId === id) {
      setActiveSessionId(newSessions.length > 0 ? newSessions[0].id : "");
    }
    setMenuOpenId(null);
  };

  const sortedSessions = [...sessions].sort((a, b) => (b.isPinned ? 1 : 0) - (a.isPinned ? 1 : 0));
  const activeSession = sessions.find(s => s.id === activeSessionId) || (sessions.length > 0 ? sessions[0] : null);
  const messages = activeSession ? activeSession.messages : [];

  return (
    <div className="container">
      <aside className="sidebar">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <span>+</span> New Chat
        </button>

        <h3>Recent Conversations</h3>
        <div className="history-container">
          {sortedSessions.map((s) => (
            <div
              key={s.id}
              className={`history-item ${activeSessionId === s.id ? 'active' : ''}`}
              onClick={() => setActiveSessionId(s.id)}
            >
              <span className="chat-item-text">
                {s.isPinned && <span className="pinned-badge">📌</span>}
                {s.title}
              </span>
              <div className="menu-trigger" onClick={(e) => toggleMenu(e, s.id)}>⋮</div>

              {menuOpenId === s.id && (
                <div className="options-dropdown" onClick={(e) => e.stopPropagation()}>
                  <div className="dropdown-item" onClick={() => startRename(s.id, s.title)}>✏️ Rename</div>
                  <div className="dropdown-item" onClick={() => handlePin(s.id)}>
                    {s.isPinned ? "📍 Unpin" : "📌 Pin Chat"}
                  </div>
                  <div className="dropdown-item delete" onClick={(e) => handleDelete(e, s.id)}>🗑️ Delete</div>
                </div>
              )}
            </div>
          ))}
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          Logout 🚪
        </button>
      </aside>

      <main className="chat-section">
        <div className="chat-content-container">
          <header className="chat-header">
            <h1>DocuMind AI 🤖</h1>
            <div className="upload-card">
              <input type="file" onChange={(e) => setFile(e.target.files[0])} />
              <button className="primary-btn" onClick={handleUpload}>
                ✨ Upload PDF
              </button>
            </div>

            <div className="quick-actions">
              <button onClick={() => askAI("Summarize this document in 3-5 concise sentences.")}>✨ Summarize</button>
              <button onClick={() => askAI("What are the 5 most important key points from this document?")}>📌 Key Points</button>
              <button onClick={() => askAI("Explain the core concept of this document in simple terms.")}>🧠 Explain</button>
              <button onClick={() => askAI("What are the deepest AI-generated insights or opportunities mentioned here?")}>💡 Insights</button>
            </div>
          </header>

          <div className="chat-box" ref={chatBoxRef}>
            {messages.length === 0 && !loading && (
              <div className="ai" style={{ alignSelf: 'center', textAlign: 'center', opacity: 0.6, background: 'transparent', boxShadow: 'none' }}>
                Welcome! Start a new conversation or upload a PDF. ✨
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={msg.role}>{msg.text}</div>
            ))}
            {loading && <div className="ai"><span className="dot-animation">AI is thinking...</span></div>}
          </div>

          <footer className="chat-footer">
            <div className="input-box">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                placeholder="Ask DocuMind AI..."
              />
              <button className="send-btn" onClick={handleAsk}>➤</button>
            </div>
          </footer>
        </div>
      </main>
    </div>
  );
}

// Final App with Routing
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ChatInterface />
            </ProtectedRoute>
          }
        />
        {/* Redirect any other path to home/chat */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;