import React from "react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
         <span>CNAB</span> Parser
      </div>
      {user && (
        <div className="navbar-user">
          {user.picture && <img src={user.picture} alt={user.name} />}
          <span>{user.name}</span>
          <button className="btn btn-ghost" style={{ padding: "0.35rem 0.8rem" }} onClick={logout}>
            Sair
          </button>
        </div>
      )}
    </nav>
  );
}
