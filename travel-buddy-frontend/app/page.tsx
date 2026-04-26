"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type UserProfile = {
  name: string;
  email: string;
};

export default function Home() {
  const [user] = useState<UserProfile | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }

    const savedUser = sessionStorage.getItem("travelBuddyUser");
    return savedUser ? (JSON.parse(savedUser) as UserProfile) : null;
  });

  useEffect(() => {
    localStorage.removeItem("travelBuddyUser");
  }, []);

  return (
    <main className="landing-shell">
      <section className="hero-card">
        <nav className="top-nav">
          <div className="brand-mark">Travel Buddy</div>
          <div className="nav-links">
            <Link href="/">Home</Link>
            {user ? <Link href="/profile">Profile</Link> : <Link href="/login">Login</Link>}
            {!user ? <Link href="/register">Register</Link> : <Link href="/planner">Planner</Link>}
          </div>
        </nav>

        <div className="hero-grid">
          <div>
            <p className="eyebrow">AI itinerary planner</p>
            <h1 className="hero-title">
              &ldquo;Turn your travel ideas into smart itineraries.&rdquo;
            </h1>
            <p className="hero-copy">
              Plan destinations, estimate your budget, view hotel and restaurant
              suggestions, and organize a trip experience you can confidently
              demo as your final project.
            </p>

            <div className="hero-actions">
              {user ? (
                <Link className="primary-link" href="/planner">
                  Open planner
                </Link>
              ) : (
                <Link className="primary-link" href="/login">
                  Login to continue
                </Link>
              )}
              <Link className="secondary-link" href={user ? "/profile" : "/register"}>
                {user ? "View profile" : "Create account"}
              </Link>
            </div>
          </div>

          <div className="hero-panel">
            <div className="hero-panel-badge">Sample trip</div>
            <h2>Goa, 3 Days, Medium Budget</h2>
            <ul className="feature-list">
              <li>Beach day, local market, and sunset cruise itinerary</li>
              <li>Hotel picks from guesthouses to boutique stays</li>
              <li>Restaurant suggestions for breakfast, lunch, and dinner</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="highlights-grid">
        <article className="highlight-card">
          <h3>Budget-smart stays</h3>
          <p>See hotel picks that fit student, mid-range, or premium travel budgets.</p>
        </article>
        <article className="highlight-card">
          <h3>Food nearby</h3>
          <p>Get restaurant suggestions for every day of the plan without hunting manually.</p>
        </article>
        <article className="highlight-card">
          <h3>Secure flow</h3>
          <p>Planner and profile access now open only after login so the app feels complete.</p>
        </article>
      </section>
    </main>
  );
}
