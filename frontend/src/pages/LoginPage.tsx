import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { AgentStage } from "../components/AgentStage";
import { Button } from "../components/Button";
import { TextField } from "../components/Field";
import { Wordmark } from "../layout/AppNav";
import styles from "./pages.module.css";

export function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);

  const from = (location.state as { from?: string } | null)?.from ?? "/agents";
  if (isAuthenticated) return <Navigate to={from} replace />;

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(undefined);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError && err.status === 401 ? "Email o contraseña incorrectos." : "No se pudo ingresar. Probá de nuevo.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={`container ${styles.login}`}>
      <main className={styles.loginMain}>
        <Wordmark />
        <div>
          <span className="eyebrow">Plataforma de cobranza</span>
          <h1 className="enter">Ingresá a Kleva.</h1>
          <p className={`enter ${styles.loginIntro}`}>
            Configurá tus agentes de cobranza, activalos y mirá cada llamada en vivo.
          </p>
        </div>
        <form className={`card ${styles.loginForm}`} onSubmit={onSubmit} noValidate>
          <TextField
            label="Email"
            type="email"
            autoComplete="username"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            label="Contraseña"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && (
            <p className={styles.alert} role="alert">
              {error}
            </p>
          )}
          <Button type="submit" full arrow disabled={submitting || !email || !password}>
            {submitting ? "Ingresando…" : "Ingresar"}
          </Button>
          <p className={styles.loginHint}>
            Demo: <span className="mono">admin@kleva.demo</span> / <span className="mono">Kleva2026</span>
          </p>
        </form>
      </main>
      <div className={styles.loginStage}>
        <AgentStage live />
      </div>
    </div>
  );
}
