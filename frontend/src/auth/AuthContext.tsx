import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { fetchMe, login as loginRequest } from "../api/auth";
import { setUnauthorizedHandler, tokenStore } from "../api/client";
import type { KlevaUser } from "../api/types";

interface AuthState {
  user: KlevaUser | undefined;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState(() => tokenStore.get());

  const logout = useCallback(() => {
    tokenStore.clear();
    setToken(null);
    queryClient.clear();
  }, [queryClient]);

  useEffect(() => setUnauthorizedHandler(logout), [logout]);

  const me = useQuery({ queryKey: ["me", token], queryFn: fetchMe, enabled: Boolean(token), retry: false });

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await loginRequest(email, password);
    tokenStore.set(access_token);
    setToken(access_token);
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      user: me.data,
      isAuthenticated: Boolean(token),
      isLoading: Boolean(token) && me.isLoading,
      login,
      logout,
    }),
    [me.data, me.isLoading, token, login, logout],
  );

  return <AuthContext value={value}>{children}</AuthContext>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth fuera de AuthProvider");
  return context;
}
