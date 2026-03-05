import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import ParentDashboard from "./pages/ParentDashboard";
import NutritionWorkerDashboard from "./pages/NutritionWorkerDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import { isAuthenticated, getUserRole, getRoleBasedRoute } from "./utils/auth";

// Protected Route Component
function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/" replace />;
  }
  return children;
}

// Role-based Redirect Component
function RoleBasedRedirect() {
  const role = getUserRole();
  if (!role) return <Navigate to="/" replace />;
  return <Navigate to={getRoleBasedRoute(role)} replace />;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      
      {/* Legacy dashboard route - redirects to role-based dashboard */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <RoleBasedRedirect />
          </ProtectedRoute>
        } 
      />
      
      {/* Role-specific dashboards */}
      <Route 
        path="/dashboard/parent" 
        element={
          <ProtectedRoute>
            <ParentDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard/nutrition-worker" 
        element={
          <ProtectedRoute>
            <NutritionWorkerDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard/admin" 
        element={
          <ProtectedRoute>
            <AdminDashboard />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}

export default App;

