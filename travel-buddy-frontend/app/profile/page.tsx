"use client";

import Link from "next/link";
import { useState } from "react";
import AuthGuard from "../components/AuthGuard";

type UserProfile = {
  name: string;
  email: string;
};

export default function ProfilePage() {
  const [user] = useState<UserProfile | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }

    const savedUser = sessionStorage.getItem("travelBuddyUser");
    return savedUser ? (JSON.parse(savedUser) as UserProfile) : null;
  });

  const logout = () => {
    sessionStorage.removeItem("travelBuddyUser");
    localStorage.removeItem("travelBuddyUser");
    window.location.href = "/";
  };

  return (
    <AuthGuard>
      <main className="app-shell">
        <section className="planner-header">
          <div>
            <p className="eyebrow">Your account</p>
            <h1 className="section-title">Traveler profile</h1>
          </div>
          <div className="nav-links">
            <Link href="/">Home</Link>
            <Link href="/planner">Planner</Link>
          </div>
        </section>

        <section className="profile-card">
          <div className="profile-avatar">{user?.name?.charAt(0).toUpperCase() || "T"}</div>
          <h2>{user?.name || "Traveler"}</h2>
          <p className="inline-note">{user?.email || "Login to view your profile details."}</p>

          <div className="profile-grid">
            <article className="highlight-card">
              <h3>Account status</h3>
              <p>Logged in and ready to continue trip planning.</p>
            </article>
            <article className="highlight-card">
              <h3>Next step</h3>
              <p>Open the planner and generate a travel itinerary with budget-based stays.</p>
            </article>
            <article className="highlight-card">
              <h3>Project flow</h3>
              <p>Landing page, auth flow, profile page, and planner are now connected.</p>
            </article>
          </div>

          <div className="hero-actions">
            <Link className="primary-link" href="/planner">
              Open planner
            </Link>
            <button className="secondary-button" onClick={logout}>
              Logout
            </button>
          </div>
        </section>
      </main>
    </AuthGuard>
  );
}
