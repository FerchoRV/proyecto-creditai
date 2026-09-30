"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { clearSession, getStoredUser, getToken } from "@/lib/auth";
import type { User } from "@/lib/api";

export function AuthNav() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (getToken()) {
      setUser(getStoredUser());
    }
  }, []);

  function logout() {
    clearSession();
    setUser(null);
    window.location.href = "/";
  }

  return (
    <nav className="auth-nav" aria-label="Cuenta">
      {user ? (
        <>
          <Link href="/cuenta">{user.nombre}</Link>
          <button type="button" className="linkish" onClick={logout}>
            Salir
          </button>
        </>
      ) : (
        <>
          <Link href="/login">Iniciar sesión</Link>
          <Link href="/registro" className="btn-primary">
            Registrarse
          </Link>
        </>
      )}
    </nav>
  );
}
