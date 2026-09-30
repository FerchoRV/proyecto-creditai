"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import {
  ApiError,
  apiFetch,
  type SolicitudDetail,
  type SolicitudEstado,
  type User,
} from "@/lib/api";
import { clearSession, getStoredUser, getToken } from "@/lib/auth";

function formatDate(value: string): string {
  try {
    return new Date(value).toLocaleString("es-CO", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return value;
  }
}

function labelEstado(estado: SolicitudEstado | null): string {
  if (!estado) return "inicio";
  return estado.replace("_", " ");
}

export default function SolicitudDetallePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [detail, setDetail] = useState<SolicitudDetail | null>(null);
  const [nuevoEstado, setNuevoEstado] = useState<SolicitudEstado | "">("");
  const [nota, setNota] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    const token = getToken();
    const stored = getStoredUser();
    if (!token || !stored) {
      router.replace("/login");
      return;
    }
    setUser(stored);
    const data = await apiFetch<SolicitudDetail>(
      `/api/v1/solicitudes/${params.id}`,
      {},
      token,
    );
    setDetail(data);
    setNuevoEstado(data.transiciones_disponibles[0] ?? "");
  }, [params.id, router]);

  useEffect(() => {
    load().catch((err) => {
      if (err instanceof ApiError && err.status === 401) {
        clearSession();
        router.replace("/login");
        return;
      }
      if (err instanceof ApiError && err.status === 403) {
        setError("No tienes acceso a esta solicitud.");
        return;
      }
      setError(err instanceof ApiError ? err.message : "No se pudo cargar");
    });
  }, [load, router]);

  async function onTransition(e: FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !nuevoEstado) return;

    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await apiFetch<SolicitudDetail>(
        `/api/v1/solicitudes/${params.id}/transiciones`,
        {
          method: "POST",
          body: JSON.stringify({
            nuevo_estado: nuevoEstado,
            nota: nota.trim() || null,
          }),
        },
        token,
      );
      setDetail(updated);
      setNota("");
      setNuevoEstado(updated.transiciones_disponibles[0] ?? "");
      setMessage("Estado actualizado.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo actualizar");
    } finally {
      setLoading(false);
    }
  }

  if (!detail && !error) {
    return (
      <main className="form-page">
        <p className="tagline">Cargando solicitud…</p>
      </main>
    );
  }

  return (
    <main className="form-page wide">
      <p className="eyebrow">
        <Link href="/procesos">← Procesos</Link>
      </p>
      <h1>Solicitud #{params.id}</h1>
      {detail ? (
        <p className="tagline">
          Estado actual: <strong>{labelEstado(detail.estado)}</strong>
          {" · "}
          Asesor #{detail.asesor_id}
          {detail.cliente_id ? ` · Cliente #${detail.cliente_id}` : " · sin cliente"}
        </p>
      ) : null}

      {detail ? (
        <>
          <h2 className="section-title">Línea de tiempo</h2>
          <ol className="timeline">
            {detail.timeline.map((event) => (
              <li key={event.id}>
                <div className="timeline-dot" aria-hidden />
                <div className="timeline-body">
                  <strong>
                    {labelEstado(event.from_state)} → {labelEstado(event.to_state)}
                  </strong>
                  <span className="muted">
                    {formatDate(event.created_at)} · actor #{event.actor_id}
                  </span>
                  {event.nota ? <p className="timeline-note">{event.nota}</p> : null}
                </div>
              </li>
            ))}
          </ol>

          {user?.rol === "asesor" && detail.transiciones_disponibles.length > 0 ? (
            <>
              <h2 className="section-title">Cambiar estado</h2>
              <form className="stack-form" onSubmit={onTransition}>
                <label>
                  Nuevo estado
                  <select
                    value={nuevoEstado}
                    onChange={(e) =>
                      setNuevoEstado(e.target.value as SolicitudEstado)
                    }
                    required
                  >
                    {detail.transiciones_disponibles.map((estado) => (
                      <option key={estado} value={estado}>
                        {labelEstado(estado)}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Nota (opcional)
                  <input
                    maxLength={280}
                    value={nota}
                    onChange={(e) => setNota(e.target.value)}
                    placeholder="Motivo breve del cambio"
                  />
                </label>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? "Guardando…" : "Aplicar transición"}
                </button>
              </form>
            </>
          ) : null}

          {user?.rol === "asesor" && detail.transiciones_disponibles.length === 0 ? (
            <p className="tagline">Esta solicitud está en un estado final.</p>
          ) : null}

          {user?.rol === "cliente" ? (
            <p className="tagline">Solo lectura: el asesor gestiona los cambios de estado.</p>
          ) : null}
        </>
      ) : null}

      {message ? <p className="form-ok">{message}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}
    </main>
  );
}
