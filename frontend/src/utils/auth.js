// Auth utility functions for handling JWT token and role-based access

const TOKEN_KEY = 'nutrition_jwt_token';
const USER_KEY = 'nutrition_user';

export const setAuthData = (token, user) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const getJwtToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const getUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
};

export const getUserRole = () => {
  const user = getUser();
  return user ? user.role : null;
};

export const getUserName = () => {
  const user = getUser();
  return user ? user.name : null;
};

export const isAuthenticated = () => {
  return getJwtToken() !== null;
};

export const isJwtValid = () => {
  const token = getJwtToken();
  if (!token) return false;
  try {
    // Decode JWT payload (client-side validation)
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
};

export const hasRole = (role) => {
  return getUserRole() === role;
};

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

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

export const getAuthHeaders = () => {
  const token = getJwtToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};


