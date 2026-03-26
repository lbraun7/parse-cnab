import { useState, useCallback } from "react";
import api from "../services/api";

export function useTransactions() {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStores = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get("/transactions/stores");
      setStores(data.stores);
    } catch (e) {
      setError(e.response?.data?.detail || "Erro ao carregar transações");
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadCNAB = useCallback(async (file) => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post("/transactions/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  }, []);

  return { stores, loading, error, fetchStores, uploadCNAB };
}
