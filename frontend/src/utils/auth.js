// Auth utility functions for handling user authentication and role-based access

const USER_KEY = 'nutrition_user';

// Save user info to localStorage
export const setUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

// Get user info from localStorage
export const getUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
};

// Get current user role
export const getUserRole = () => {
  const user = getUser();
  return user ? user.role : null;
};

// Get current user name
export const getUserName = () => {
  const user = getUser();
  return user ? user.name : null;
};

// Check if user is logged in
export const isAuthenticated = () => {
  return getUser() !== null;
};

// Check if user has specific role
export const hasRole = (role) => {
  return getUserRole() === role;
};

// Clear user info (logout)
export const logout = () => {
  localStorage.removeItem(USER_KEY);
};

// Get redirect path based on role
export const getRoleBasedRoute = (role) => {
  switch (role) {
    case 'parent':
      return '/dashboard/parent';
    case 'nutrition_worker':
      return '/dashboard/nutrition-worker';
    case 'admin':
      return '/dashboard/admin';
    default:
      return '/dashboard';
  }
};

