import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

const Signup = () => {
  const [formData, setFormData] = useState({
    username: "",
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirm_password) {
      return setError("Passwords do not match");
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/accounts/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: formData.username,
          full_name: formData.full_name,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("documind_token", data.access);
        localStorage.setItem("documind_refresh", data.refresh);
        localStorage.setItem("documind_user_email", data.email);
        alert("Account created successfully! Please login.");
        navigate("/login");
      } else {
        const errorMsg = Object.values(data).flat().join(" ") || "Registration failed";
        setError(errorMsg);
      }
    } catch (err) {
      setError("Server connection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split">
      {/* LEFT — Illustration Panel */}
      <div className="auth-hero">
        <img src="/astronaut.png" alt="InsightLens" className="auth-hero-img" />
        <div className="auth-hero-overlay">
          <h2>Start Your<br />Journey Today</h2>
          <p>Join thousands using AI-powered documents</p>
        </div>
      </div>

      {/* RIGHT — Form Panel (ALL LOGIC IDENTICAL) */}
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1 className="brand-title-auth">Insight<span className="brand-accent-auth">Lens</span></h1>
            <p className="auth-subtitle">Get started with InsightLens for free</p>
          </div>

          <form onSubmit={handleSignup} className="auth-form">
            <div className="form-group">
              <label>Choose Username</label>
              <input
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                placeholder="e.g. jdoe123"
                required
              />
            </div>

            <div className="form-group">
              <label>Full Name</label>
              <input
                name="full_name"
                type="text"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="form-group">
              <label>Email Address</label>
              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
              />
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input
                name="confirm_password"
                type="password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="••••••••"
                required
              />
            </div>

            {error && <div className="auth-error">{error}</div>}

            <button type="submit" className="auth-submit-btn" disabled={loading}>
              {loading ? "Creating account..." : "Sign up"}
            </button>
          </form>

          <div className="auth-footer">
            Already have an account? <Link to="/login">Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
