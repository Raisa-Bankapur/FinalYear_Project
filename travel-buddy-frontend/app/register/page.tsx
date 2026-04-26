"use client";

import Link from "next/link";
import { useState } from "react";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleRegister = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();
      setMessage(data.message || "Registration complete");
    } catch {
      setMessage("Backend is not available right now.");
    }
  };

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="eyebrow">Create account</p>
        <h1 className="section-title">Start building your travel profile</h1>
        <p className="auth-copy">
          Save your future itineraries and make the project feel like a real app.
        </p>

        <label className="field-label" htmlFor="name">
          Full name
        </label>
        <input
          id="name"
          className="input-field"
          placeholder="Your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <label className="field-label" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          className="input-field"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="field-label" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          className="input-field"
          placeholder="Create a password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="primary-button" onClick={handleRegister}>
          Register
        </button>

        {message ? <p className="inline-note">{message}</p> : null}

        <p className="auth-footer">
          Already have an account? <Link href="/login">Login here</Link>
        </p>
        <p className="auth-footer">
          <Link href="/">Back to home</Link>
        </p>
      </section>
    </main>
  );
}
