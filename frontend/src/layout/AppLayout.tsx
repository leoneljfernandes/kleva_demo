import { Outlet } from "react-router";
import { AppNav } from "./AppNav";

export function AppLayout() {
  return (
    <>
      <AppNav />
      <main className="container page">
        <Outlet />
      </main>
    </>
  );
}
