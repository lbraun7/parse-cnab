import React, { useRef, useState } from "react";

export default function UploadZone({ onFile, loading }) {
  const inputRef = useRef();
  const [drag, setDrag] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDrag(false);
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  };

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) onFile(file);
  };

  return (
    <div
      className={`upload-zone ${drag ? "drag-over" : ""}`}
      onClick={() => !loading && inputRef.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
    >
      <input ref={inputRef} type="file" accept=".txt" onChange={handleChange} />

      {loading ? (
        <>
          <div className="upload-icon">⏳</div>
          <strong>Importando...</strong>
          <p>Aguarde enquanto processamos o arquivo</p>
        </>
      ) : (
        <>
          <div className="upload-icon">📂</div>
          <strong>Arraste o arquivo CNAB aqui</strong>
          <p>ou clique para selecionar — apenas arquivos <strong>.txt</strong></p>
        </>
      )}
    </div>
  );
}
