"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import {
  ApiError,
  apiFetch,
  type AuthResponse,
  type TipoIdentificacion,
  type TipoPrestamo,
  type UserRole,
} from "@/lib/api";
import { saveSession } from "@/lib/auth";

export default function RegistroPage() {
  const router = useRouter();
  const [rol, setRol] = useState<UserRole>("asesor");
  const [nombre, setNombre] = useState("");
  const [tipoIdentificacion, setTipoIdentificacion] =
    useState<TipoIdentificacion>("CC");
  const [numeroIdentificacion, setNumeroIdentificacion] = useState("");
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [salario, setSalario] = useState("");
  const [tipoPrestamo, setTipoPrestamo] = useState<TipoPrestamo>("libranza");
  const [montoPrestamo, setMontoPrestamo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const body: Record<string, unknown> = {
      nombre,
      tipo_identificacion: tipoIdentificacion,
      numero_identificacion: numeroIdentificacion,
      correo,
      password,
      rol,
    };

    if (rol === "cliente") {
      body.salario = Number(salario);
      body.tipo_prestamo = tipoPrestamo;
      body.monto_prestamo = Number(montoPrestamo);
    }

    try {
      const auth = await apiFetch<AuthResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(body),
      });
      saveSession(auth);
      router.push("/cuenta");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo registrar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="form-page">
      <p className="eyebrow">
        <Link href="/">CreditAI</Link>
      </p>
      <h1>Crear cuenta</h1>
      <p className="tagline">
        Elige tu rol. Asesores y clientes se registran por separado.
      </p>

      <div className="role-switch" role="group" aria-label="Rol">
        <button
          type="button"
          className={rol === "asesor" ? "active" : ""}
          onClick={() => setRol("asesor")}
        >
          Asesor
        </button>
        <button
          type="button"
          className={rol === "cliente" ? "active" : ""}
          onClick={() => setRol("cliente")}
        >
          Cliente
        </button>
      </div>

      <form className="stack-form" onSubmit={onSubmit}>
        <label>
          Nombre
          <input
            required
            minLength={2}
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
          />
        </label>

        <div className="row-2">
          <label>
            Tipo ID
            <select
              value={tipoIdentificacion}
              onChange={(e) =>
                setTipoIdentificacion(e.target.value as TipoIdentificacion)
              }
            >
              <option value="CC">CC</option>
              <option value="CE">CE</option>
              <option value="PA">Pasaporte</option>
              <option value="NIT">NIT</option>
            </select>
          </label>
          <label>
            Número
            <input
              required
              minLength={3}
              value={numeroIdentificacion}
              onChange={(e) => setNumeroIdentificacion(e.target.value)}
            />
          </label>
        </div>

        <label>
          Correo
          <input
            type="email"
            required
            autoComplete="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
          />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            required
            minLength={8}
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        {rol === "cliente" ? (
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

        {error ? <p className="form-error">{error}</p> : null}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Registrando…" : "Registrarme"}
        </button>
      </form>

      <p className="form-footer">
        ¿Ya tienes cuenta? <Link href="/login">Inicia sesión</Link>
      </p>
    </main>
  );
}
