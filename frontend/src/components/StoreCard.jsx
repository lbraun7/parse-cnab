import React, { useState } from "react";

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

function formatDate(iso) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatCPF(cpf) {
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

export default function StoreCard({ store }) {
  const [open, setOpen] = useState(false);
  const isPositive = parseFloat(store.balance) >= 0;

  return (
    <div className="store-card">
      <div className="store-header" onClick={() => setOpen((o) => !o)}>
        <div className="store-info">
          <h3>{store.store_name}</h3>
          <small>
            Responsável: {store.store_owner} · {store.transactions.length} transação(ões)
          </small>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span className={`store-balance ${isPositive ? "positive" : "negative"}`}>
            {formatCurrency(store.balance)}
          </span>
          <span className={`store-chevron ${open ? "open" : ""}`}>▼</span>
        </div>
      </div>

      {open && (
        <div className="tx-table-wrap">
          <table className="tx-table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Descrição</th>
                <th>Natureza</th>
                <th>Data / Hora</th>
                <th>Valor</th>
                <th>CPF</th>
                <th>Cartão</th>
              </tr>
            </thead>
            <tbody>
              {store.transactions.map((tx) => {
                const nature = tx.transaction_type?.nature ?? "entrada";
                const description = tx.transaction_type?.description ?? "-";
                const typeId = tx.transaction_type_id;

                return (
                  <tr key={tx.id}>
                    <td style={{ color: "var(--text-muted)" }}>#{typeId}</td>
                    <td>{description}</td>
                    <td>
                      <span className={`badge badge-${nature}`}>
                        {nature === "entrada" ? "↑ Entrada" : "↓ Saída"}
                      </span>
                    </td>
                    <td>{formatDate(tx.occurred_at)}</td>
                    <td style={{ fontWeight: 600 }}>
                      <span
                        style={{
                          color:
                            nature === "entrada"
                              ? "var(--success)"
                              : "var(--danger)",
                        }}
                      >
                        {nature === "entrada" ? "+" : "-"}
                        {formatCurrency(tx.amount)}
                      </span>
                    </td>
                    <td style={{ color: "var(--text-muted)", fontFamily: "monospace" }}>
                      {formatCPF(tx.cpf)}
                    </td>
                    <td style={{ color: "var(--text-muted)", fontFamily: "monospace" }}>
                      {tx.card}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
