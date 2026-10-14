import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Link, type LinkProps } from "react-router";
import styles from "./Button.module.css";

type Variant = "primary" | "secondary" | "link";

interface StyleProps {
  variant?: Variant;
  size?: "md" | "sm";
  full?: boolean;
  arrow?: boolean; // "→" de los CTA: es texto, no ícono
}

export function buttonClass({ variant = "primary", size = "md", full = false }: StyleProps = {}) {
  return [styles.button, styles[variant], size === "sm" && styles.sm, full && styles.full].filter(Boolean).join(" ");
}

function Content({ children, arrow }: { children: ReactNode; arrow?: boolean }) {
  return (
    <>
      {children}
      {arrow && (
        <span className={styles.arrow} aria-hidden="true">
          →
        </span>
      )}
    </>
  );
}

export function Button({
  variant,
  size,
  full,
  arrow,
  className,
  children,
  type = "button",
  ...props
}: StyleProps & ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button type={type} className={[buttonClass({ variant, size, full }), className].filter(Boolean).join(" ")} {...props}>
      <Content arrow={arrow}>{children}</Content>
    </button>
  );
}

export function ButtonLink({ variant, size, full, arrow, children, ...props }: StyleProps & LinkProps) {
  return (
    <Link className={buttonClass({ variant, size, full })} {...props}>
      <Content arrow={arrow}>{children}</Content>
    </Link>
  );
}
