import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ParentDashboard from "./pages/ParentDashboard";
import NutritionWorkerDashboard from "./pages/NutritionWorkerDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import { isAuthenticated, getUserRole } from "./utils/auth";

function ProtectedRoute({ children, allowedRoles }) {
  if (!isAuthenticated()) return <Navigate to="/" />;
  const role = getUserRole();
  if (allowedRoles && !allowedRoles.includes(role)) {
    switch (role) {
      case 'parent': return <Navigate to="/dashboard/parent" />;
      case 'nutrition_worker': return <Navigate to="/dashboard/nutrition-worker" />;
      case 'admin': return <Navigate to="/dashboard/admin" />;
      default: return <Navigate to="/" />;
    }
  }
  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/dashboard/parent" element={
        <ProtectedRoute allowedRoles={['parent']}>
          <ParentDashboard />
        </ProtectedRoute>
      } />
      <Route path="/dashboard/nutrition-worker" element={
        <ProtectedRoute allowedRoles={['nutrition_worker']}>
          <NutritionWorkerDashboard />
        </ProtectedRoute>
      } />
      <Route path="/dashboard/admin" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <AdminDashboard />
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
