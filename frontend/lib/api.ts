const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type UserRole = "asesor" | "cliente";
export type TipoIdentificacion = "CC" | "CE" | "PA" | "NIT";
export type TipoPrestamo = "hipotecario" | "libranza" | "libre_inversion";

export type User = {
  id: number;
  nombre: string;
  tipo_identificacion: TipoIdentificacion;
  numero_identificacion: string;
  correo: string;
  rol: UserRole;
  salario: number | null;
  tipo_prestamo: TipoPrestamo | null;
  monto_prestamo: number | null;
  activo: boolean;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type SolicitudEstado =
  | "recibido"
  | "en_estudio"
  | "aprobado"
  | "rechazado";

export type InvitacionEstado = "pendiente" | "vinculada";

export type Solicitud = {
  id: number;
  asesor_id: number;
  cliente_id: number | null;
  estado: SolicitudEstado;
  created_at: string;
  updated_at: string;
};

export type Invitation = {
  id: number;
  asesor_id: number;
  solicitud_id: number;
  correo_objetivo: string | null;
  tipo_identificacion: TipoIdentificacion | null;
  numero_identificacion: string | null;
  estado: InvitacionEstado;
  created_at: string;
  solicitud: Solicitud;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as {
      detail?: string | Array<{ msg?: string }>;
    };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return data.detail.map((d) => d.msg).join(". ");
    }
  } catch {
    /* ignore */
  }
  return `Error ${res.status}`;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    throw new ApiError(res.status, await parseError(res));
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export { API_URL };
