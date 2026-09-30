import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CreditAI",
  description: "Plataforma para asesores de crédito y solicitantes",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
