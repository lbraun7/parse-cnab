import React, { useEffect, useState } from "react";
import UploadZone from "../components/UploadZone";
import StoreCard from "../components/StoreCard";
import { useTransactions } from "../hooks/useTransactions";

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

export default function DashboardPage() {
  const { stores, loading, error, fetchStores, uploadCNAB } = useTransactions();
  const [uploading, setUploading] = useState(false);
  const [alert, setAlert] = useState(null);

  useEffect(() => { fetchStores(); }, [fetchStores]);

  const handleFile = async (file) => {
    setAlert(null);
    setUploading(true);
    try {
      const result = await uploadCNAB(file);
      setAlert({ type: "success", msg: result.message });
      fetchStores();
    } catch (e) {
      const detail = e.response?.data?.detail;
      const msg = Array.isArray(detail)
        ? detail.map((d) => d.msg).join(", ")
        : detail || "Erro ao importar arquivo";
      setAlert({ type: "error", msg });
    } finally {
      setUploading(false);
    }
  };

  const totalBalance = stores.reduce((acc, s) => acc + parseFloat(s.balance), 0);
  const totalTransactions = stores.reduce((acc, s) => acc + s.transactions.length, 0);

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Importe um arquivo CNAB e visualize as transações por loja</p>
      </div>

      {stores.length > 0 && (
        <div className="summary-row">
          <div className="summary-card">
            <div className="label">Lojas</div>
            <div className="value">{stores.length}</div>
          </div>
          <div className="summary-card">
            <div className="label">Transações</div>
            <div className="value">{totalTransactions}</div>
          </div>
          <div className="summary-card">
            <div className="label">Saldo Geral</div>
            <div
              className="value"
              style={{ color: totalBalance >= 0 ? "var(--success)" : "var(--danger)" }}
            >
              {formatCurrency(totalBalance)}
            </div>
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: "2rem" }}>
        <div className="card-title">Importar Arquivo CNAB</div>

        {alert && (
          <div className={`alert alert-${alert.type}`}>
            {alert.type === "success" ? "✅" : "❌"} {alert.msg}
          </div>
        )}

        <UploadZone onFile={handleFile} loading={uploading} />
      </div>

      <div className="card-title" style={{ marginBottom: "1rem" }}>
        Transações por Loja
      </div>

      {loading ? (
        <div className="loading-center">
          <div className="spinner" />
        </div>
      ) : error ? (
        <div className="alert alert-error">❌ {error}</div>
      ) : stores.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>Nenhuma transação encontrada</h3>
          <p>Faça o upload de um arquivo CNAB para começar</p>
        </div>
      ) : (
        <div className="stores-grid">
          {stores.map((store) => (
            <StoreCard key={store.store_name} store={store} />
          ))}
        </div>
      )}
    </>
  );
}
