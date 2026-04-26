"use client";

import { useRouter } from "next/navigation";
import { ReactNode, useEffect, useSyncExternalStore } from "react";

type AuthGuardProps = {
  children: ReactNode;
};

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const ready = useSyncExternalStore(
    () => () => undefined,
    () => Boolean(sessionStorage.getItem("travelBuddyUser")),
    () => false
  );

  useEffect(() => {
    if (!ready) {
      localStorage.removeItem("travelBuddyUser");
      router.replace("/");
    }
  }, [ready, router]);

  if (!ready) {
    return (
      <main className="auth-shell">
        <section className="auth-card">
          <p className="eyebrow">Checking access</p>
          <h1 className="section-title">Redirecting...</h1>
          <p className="auth-copy">
            Please login to open the planner and profile pages.
          </p>
        </section>
      </main>
    );
  }

  return <>{children}</>;
}
