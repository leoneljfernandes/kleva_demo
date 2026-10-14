import { api } from "./client";
import type { KlevaUser, Token } from "./types";

export function login(email: string, password: string) {
  // Flujo OAuth2 password: form-urlencoded y el campo se llama "username"
  const body = new URLSearchParams({ username: email, password });
  return api<Token>("/auth/login", { method: "POST", body });
}

export function fetchMe() {
  return api<KlevaUser>("/auth/me");
}
