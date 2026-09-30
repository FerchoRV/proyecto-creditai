import { HealthStatus } from "@/components/HealthStatus";

export default function HomePage() {
  return (
    <main>
      <h1 className="brand">CreditAI</h1>
      <p className="tagline">
        Plataforma para asesores de crédito y solicitantes. Esqueleto en
        contenedores listo para las features de autenticación y gestión.
      </p>
      <HealthStatus />
    </main>
  );
}
