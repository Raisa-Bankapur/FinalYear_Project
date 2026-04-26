"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setMessage("");

    try {
      const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessage(data.message || "Login failed");
        return;
      }

      localStorage.removeItem("travelBuddyUser");
      sessionStorage.setItem(
        "travelBuddyUser",
        JSON.stringify(data.user || { name: "Traveler", email })
      );
      router.push("/profile");
    } catch {
      setMessage("Backend is not available right now.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="eyebrow">Welcome back</p>
        <h1 className="section-title">Login to your travel account</h1>
        <p className="auth-copy">
          Access saved trips, compare budgets, and continue planning.
        </p>

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
          placeholder="Enter password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="primary-button" onClick={handleLogin} disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>

        {message ? <p className="inline-note">{message}</p> : null}

        <p className="auth-footer">
          Need an account? <Link href="/register">Register here</Link>
        </p>
        <p className="auth-footer">
          <Link href="/">Back to home</Link>
        </p>
      </section>
    </main>
  );
}
