"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  ApiError,
  apiFetch,
  type TipoPrestamo,
  type User,
} from "@/lib/api";
import { clearSession, getToken, saveUser } from "@/lib/auth";

export default function CuentaPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [salario, setSalario] = useState("");
  const [tipoPrestamo, setTipoPrestamo] = useState<TipoPrestamo>("libranza");
  const [montoPrestamo, setMontoPrestamo] = useState("");
  const [passwordActual, setPasswordActual] = useState("");
  const [passwordNueva, setPasswordNueva] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    apiFetch<User>("/api/v1/users/me", {}, token)
      .then((profile) => {
        setUser(profile);
        setNombre(profile.nombre);
        setCorreo(profile.correo);
        setSalario(profile.salario != null ? String(profile.salario) : "");
        setTipoPrestamo(profile.tipo_prestamo ?? "libranza");
        setMontoPrestamo(
          profile.monto_prestamo != null ? String(profile.monto_prestamo) : "",
        );
        saveUser(profile);
      })
      .catch((err) => {
        clearSession();
        setError(err instanceof ApiError ? err.message : "Sesión inválida");
        router.replace("/login");
      });
  }, [router]);

  async function onSaveProfile(e: FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !user) return;

    setLoading(true);
    setError(null);
    setMessage(null);

    const body: Record<string, unknown> = { nombre, correo };
    if (user.rol === "cliente") {
      body.salario = Number(salario);
      body.tipo_prestamo = tipoPrestamo;
      body.monto_prestamo = Number(montoPrestamo);
    }

    try {
      const updated = await apiFetch<User>(
        "/api/v1/users/me",
        { method: "PATCH", body: JSON.stringify(body) },
        token,
      );
      setUser(updated);
      saveUser(updated);
      setMessage("Perfil actualizado.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar");
    } finally {
      setLoading(false);
    }
  }

  async function onChangePassword(e: FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token) return;

    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      await apiFetch<User>(
        "/api/v1/users/me/password",
        {
          method: "POST",
          body: JSON.stringify({
            password_actual: passwordActual,
            password_nueva: passwordNueva,
          }),
        },
        token,
      );
      setPasswordActual("");
      setPasswordNueva("");
      setMessage("Contraseña actualizada.");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "No se pudo cambiar la contraseña",
      );
    } finally {
      setLoading(false);
    }
  }

  async function onDeactivate() {
    const token = getToken();
    if (!token) return;
    const ok = window.confirm(
      "¿Desactivar tu cuenta? No podrás iniciar sesión después.",
    );
    if (!ok) return;

    setLoading(true);
    setError(null);
    try {
      await apiFetch<void>("/api/v1/users/me", { method: "DELETE" }, token);
      clearSession();
      router.push("/");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "No se pudo desactivar la cuenta",
      );
      setLoading(false);
    }
  }

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
      <h1>Mi perfil</h1>
      <p className="tagline">
        Sesión como <strong>{user.rol}</strong>. La identificación no se puede
        cambiar.
      </p>

      <dl className="profile-grid">
        <div>
          <dt>Identificación (inmutable)</dt>
          <dd>
            {user.tipo_identificacion} {user.numero_identificacion}
          </dd>
        </div>
      </dl>

      <form className="stack-form" onSubmit={onSaveProfile}>
        <label>
          Nombre
          <input
            required
            minLength={2}
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
          />
        </label>
        <label>
          Correo
          <input
            type="email"
            required
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
          />
        </label>

        {user.rol === "cliente" ? (
          <>
            <label>
              Salario
              <input
                type="number"
                required
                min={0}
                step="1000"
                value={salario}
                onChange={(e) => setSalario(e.target.value)}
              />
            </label>
            <label>
              Tipo de préstamo
              <select
                value={tipoPrestamo}
                onChange={(e) => setTipoPrestamo(e.target.value as TipoPrestamo)}
              >
                <option value="hipotecario">Hipotecario</option>
                <option value="libranza">Libranza</option>
                <option value="libre_inversion">Libre inversión</option>
              </select>
            </label>
            <label>
              Monto del préstamo
              <input
                type="number"
                required
                min={1}
                step="1000"
                value={montoPrestamo}
                onChange={(e) => setMontoPrestamo(e.target.value)}
              />
            </label>
          </>
        ) : null}

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Guardando…" : "Guardar cambios"}
        </button>
      </form>

      <h2 className="section-title">Cambiar contraseña</h2>
      <form className="stack-form" onSubmit={onChangePassword}>
        <label>
          Contraseña actual
          <input
            type="password"
            required
            value={passwordActual}
            onChange={(e) => setPasswordActual(e.target.value)}
          />
        </label>
        <label>
          Contraseña nueva
          <input
            type="password"
            required
            minLength={8}
            value={passwordNueva}
            onChange={(e) => setPasswordNueva(e.target.value)}
          />
        </label>
        <button type="submit" className="btn-ghost" disabled={loading}>
          Actualizar contraseña
        </button>
      </form>

      {message ? <p className="form-ok">{message}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <div className="cta-row" style={{ marginTop: "2rem" }}>
        <button type="button" className="btn-ghost" onClick={logout}>
          Cerrar sesión
        </button>
        <button
          type="button"
          className="btn-danger"
          onClick={onDeactivate}
          disabled={loading}
        >
          Desactivar cuenta
        </button>
      </div>
    </main>
  );
}
