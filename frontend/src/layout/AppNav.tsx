import { Link, NavLink } from "react-router";
import { useAuth } from "../auth/AuthContext";
import { Button, ButtonLink } from "../components/Button";
import styles from "./AppNav.module.css";

export function Wordmark() {
  return (
    <Link to="/agents" className={styles.brand} aria-label="Kleva demo, inicio">
      <span className={styles.wordmark}>Kleva</span>
      <span className={styles.tag}>DEMO</span>
    </Link>
  );
}

export function AppNav() {
  const { user, logout } = useAuth();
  return (
    <header className={styles.nav}>
      <div className={`container ${styles.inner}`}>
        <Wordmark />
        <nav className={styles.links} aria-label="Principal">
          <NavLink to="/agents" end className={styles.link}>
            Agentes
          </NavLink>
        </nav>
        <div className={styles.right}>
          {user && <span className={styles.email}>{user.email}</span>}
          <Button variant="secondary" size="sm" onClick={logout}>
            Salir
          </Button>
          <span className={styles.cta}>
            <ButtonLink to="/agents/new" size="sm" arrow>
              Nuevo agente
            </ButtonLink>
          </span>
        </div>
      </div>
    </header>
  );
}
