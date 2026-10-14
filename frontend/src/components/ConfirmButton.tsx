import { useEffect, useState, type ComponentProps } from "react";
import { Button } from "./Button";

/** Primer click pide confirmación; el segundo (dentro de 4 s) ejecuta. Sin window.confirm. */
export function ConfirmButton({
  onConfirm,
  children,
  confirmLabel = "¿Confirmar?",
  ...props
}: Omit<ComponentProps<typeof Button>, "onClick"> & { onConfirm: () => void; confirmLabel?: string }) {
  const [armed, setArmed] = useState(false);

  useEffect(() => {
    if (!armed) return;
    const timer = setTimeout(() => setArmed(false), 4000);
    return () => clearTimeout(timer);
  }, [armed]);

  return (
    <Button
      {...props}
      aria-live="polite"
      onClick={() => {
        if (armed) {
          setArmed(false);
          onConfirm();
        } else {
          setArmed(true);
        }
      }}
    >
      {armed ? confirmLabel : children}
    </Button>
  );
}
