import { AuthNav } from "@/components/AuthNav";
import { HealthStatus } from "@/components/HealthStatus";
import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <AuthNav />
      <h1 className="brand">CreditAI</h1>
      <p className="tagline">
        Plataforma para asesores de crédito y solicitantes. Regístrate o inicia
        sesión para gestionar tu perfil.
      </p>
      <div className="cta-row">
        <Link href="/registro" className="btn-primary">
          Crear cuenta
        </Link>
        <Link href="/login" className="btn-ghost">
          Ya tengo cuenta
        </Link>
      </div>
      <HealthStatus />
    </main>
  );
}
