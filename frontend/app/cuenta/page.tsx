"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, apiFetch, type User } from "@/lib/api";
import { clearSession, getToken } from "@/lib/auth";

export default function CuentaPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    apiFetch<User>("/api/v1/auth/me", {}, token)
      .then(setUser)
      .catch((err) => {
        clearSession();
        setError(err instanceof ApiError ? err.message : "Sesión inválida");
        router.replace("/login");
      });
  }, [router]);

  function logout() {
    clearSession();
    router.push("/");
  }

  if (!user) {
    return (
      <main className="form-page">
        <p className="tagline">{error ?? "Cargando perfil…"}</p>
      </main>
    );
  }

  return (
    <main className="form-page">
      <p className="eyebrow">
        <Link href="/">CreditAI</Link>
      </p>
      <h1>Hola, {user.nombre}</h1>
      <p className="tagline">
        Sesión activa como <strong>{user.rol}</strong>.
      </p>

      <dl className="profile-grid">
        <div>
          <dt>Correo</dt>
          <dd>{user.correo}</dd>
        </div>
        <div>
          <dt>Identificación</dt>
          <dd>
            {user.tipo_identificacion} {user.numero_identificacion}
          </dd>
        </div>
        {user.rol === "cliente" ? (
          <>
            <div>
              <dt>Salario</dt>
              <dd>{user.salario ?? "—"}</dd>
            </div>
            <div>
              <dt>Préstamo</dt>
              <dd>
                {user.tipo_prestamo ?? "—"} · {user.monto_prestamo ?? "—"}
              </dd>
            </div>
          </>
        ) : null}
      </dl>

      <button type="button" className="btn-primary" onClick={logout}>
        Cerrar sesión
      </button>
    </main>
  );
}
