import { createBrowserRouter, Navigate, RouterProvider } from "react-router";
import { RequireAuth } from "./auth/RequireAuth";
import { AppLayout } from "./layout/AppLayout";
import { AgentDetailPage } from "./pages/AgentDetailPage";
import { EditAgentPage, NewAgentPage, NotFound } from "./pages/AgentFormPage";
import { AgentsPage } from "./pages/AgentsPage";
import { LoginPage } from "./pages/LoginPage";

const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="/agents" replace /> },
          { path: "agents", element: <AgentsPage /> },
          { path: "agents/new", element: <NewAgentPage /> },
          { path: "agents/:id", element: <AgentDetailPage /> },
          { path: "agents/:id/edit", element: <EditAgentPage /> },
          { path: "*", element: <NotFound /> },
        ],
      },
    ],
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
