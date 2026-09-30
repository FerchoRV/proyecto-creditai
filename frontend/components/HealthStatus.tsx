"use client";

import { useEffect, useState } from "react";

type CheckState = "pending" | "ok" | "error";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function HealthStatus() {
  const [api, setApi] = useState<CheckState>("pending");
  const [db, setDb] = useState<CheckState>("pending");

  useEffect(() => {
    let cancelled = false;

    async function run() {
      try {
        const res = await fetch(`${apiUrl}/health`);
        if (!cancelled) setApi(res.ok ? "ok" : "error");
      } catch {
        if (!cancelled) setApi("error");
      }

      try {
        const res = await fetch(`${apiUrl}/health/db`);
        if (!cancelled) {
          if (!res.ok) {
            setDb("error");
            return;
          }
          const data = (await res.json()) as { status?: string };
          setDb(data.status === "ok" ? "ok" : "error");
        }
      } catch {
        if (!cancelled) setDb("error");
      }
    }

    void run();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <ul className="status-list" aria-label="Estado de servicios">
      <li>
        <span className="label">API ({apiUrl})</span>
        <span className={`badge ${api}`}>{label(api)}</span>
      </li>
      <li>
        <span className="label">Base de datos</span>
        <span className={`badge ${db}`}>{label(db)}</span>
      </li>
    </ul>
  );
}

function label(state: CheckState): string {
  if (state === "pending") return "comprobando…";
  if (state === "ok") return "ok";
  return "error";
}
