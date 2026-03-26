import React from "react";

const BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function LoginPage() {
  const handleGoogleLogin = () => {
    window.location.href = `${BACKEND_URL}/api/auth/google/login`;
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>📄 <span>CNAB</span> Importer</h1>
        <p>
          Importe arquivos CNAB, visualize transações por loja e acompanhe
          o saldo consolidado de cada operação.
        </p>

        <button className="btn btn-google" onClick={handleGoogleLogin}>
          <img
            src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
            alt="Google"
          />
          Entrar com Google
        </button>

        <p style={{ marginTop: "1.5rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
          Autenticação segura via OAuth 2.0
        </p>
      </div>
    </div>
  );
}
