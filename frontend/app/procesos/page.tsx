"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  ApiError,
  apiFetch,
  type Invitation,
  type Solicitud,
  type TipoIdentificacion,
  type User,
} from "@/lib/api";
import { clearSession, getStoredUser, getToken } from "@/lib/auth";

export default function ProcesosPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [solicitudes, setSolicitudes] = useState<Solicitud[]>([]);
  const [correo, setCorreo] = useState("");
  const [tipoId, setTipoId] = useState<TipoIdentificacion>("CC");
  const [numeroId, setNumeroId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadData(token: string, role: User["rol"]) {
    if (role === "asesor") {
      const invs = await apiFetch<Invitation[]>("/api/v1/invitations", {}, token);
      setInvitations(invs);
    }
    const sols = await apiFetch<Solicitud[]>("/api/v1/solicitudes", {}, token);
    setSolicitudes(sols);
  }

  useEffect(() => {
    const token = getToken();
    const stored = getStoredUser();
    if (!token || !stored) {
      router.replace("/login");
      return;
    }
    setUser(stored);
    loadData(token, stored.rol).catch((err) => {
      if (err instanceof ApiError && err.status === 401) {
        clearSession();
        router.replace("/login");
        return;
      }
      setError(err instanceof ApiError ? err.message : "No se pudieron cargar procesos");
    });
  }, [router]);

  async function onInvite(e: FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token) return;

    setLoading(true);
    setError(null);
    setMessage(null);

    const body: Record<string, unknown> = {};
    if (correo.trim()) body.correo = correo.trim();
    if (numeroId.trim()) {
      body.tipo_identificacion = tipoId;
      body.numero_identificacion = numeroId.trim();
    }

    try {
      await apiFetch<Invitation>(
        "/api/v1/invitations",
        { method: "POST", body: JSON.stringify(body) },
        token,
      );
      setCorreo("");
      setNumeroId("");
      setMessage("Invitación creada.");
      await loadData(token, "asesor");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo invitar");
    } finally {
      setLoading(false);
    }
  }

  if (!user) {
    return (
      <main className="form-page">
        <p className="tagline">Cargando procesos…</p>
      </main>
    );
  }

  return (
    <main className="form-page wide">
      <p className="eyebrow">
        <Link href="/">CreditAI</Link>
      </p>
      <h1>Procesos de estudio</h1>
      <p className="tagline">
        {user.rol === "asesor"
          ? "Invita clientes y sigue el estado de vinculación de cada solicitud."
          : "Consulta los estudios en los que participas."}
      </p>

      {user.rol === "asesor" ? (
        <>
          <h2 className="section-title">Invitar cliente</h2>
          <form className="stack-form" onSubmit={onInvite}>
            <label>
              Correo del cliente
              <input
                type="email"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                placeholder="opcional si envías identificación"
              />
            </label>
            <div className="row-2">
              <label>
                Tipo ID
                <select
                  value={tipoId}
                  onChange={(e) => setTipoId(e.target.value as TipoIdentificacion)}
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
                  value={numeroId}
                  onChange={(e) => setNumeroId(e.target.value)}
                  placeholder="opcional si envías correo"
                />
              </label>
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Invitando…" : "Crear invitación"}
            </button>
          </form>

          <h2 className="section-title">Mis invitaciones</h2>
          {invitations.length === 0 ? (
            <p className="tagline">Aún no hay invitaciones.</p>
          ) : (
            <ul className="process-list">
              {invitations.map((inv) => (
                <li key={inv.id}>
                  <div>
                    <strong>
                      {inv.correo_objetivo ||
                        [inv.tipo_identificacion, inv.numero_identificacion]
                          .filter(Boolean)
                          .join(" ") ||
                        "Sin destino"}
                    </strong>
                    <span className="muted">
                      Solicitud #{inv.solicitud_id} · {inv.solicitud.estado}
                    </span>
                  </div>
                  <span className={`pill ${inv.estado}`}>{inv.estado}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      ) : null}

      <h2 className="section-title">
        {user.rol === "asesor" ? "Mis solicitudes" : "Mis estudios"}
      </h2>
      {solicitudes.length === 0 ? (
        <p className="tagline">No hay solicitudes vinculadas todavía.</p>
      ) : (
        <ul className="process-list">
          {solicitudes.map((s) => (
            <li key={s.id}>
              <div>
                <strong>Solicitud #{s.id}</strong>
                <span className="muted">
                  Asesor #{s.asesor_id}
                  {s.cliente_id ? ` · Cliente #${s.cliente_id}` : " · sin cliente"}
                </span>
              </div>
              <span className="pill">{s.estado}</span>
            </li>
          ))}
        </ul>
      )}

      {message ? <p className="form-ok">{message}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <p className="form-footer">
        <Link href="/cuenta">Volver a mi perfil</Link>
      </p>
    </main>
  );
}
