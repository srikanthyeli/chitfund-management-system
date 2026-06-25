import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import api from './api';
import toast from 'react-hot-toast';

interface User {
  id: string;
  mobile: string;
  role: string;
  organizer_id: string | null;
  name: string;
  must_change_password: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: any) => Promise<any>;
  forceLogin: (data: any) => Promise<any>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await api.get('/auth/me');
          setUser(response.data);
        } catch (error) {
          console.error("Failed to fetch user", error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials: any) => {
    try {
      const response = await api.post('/auth/login', credentials);
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      setUser(response.data.user);
      return { success: true, user: response.data.user };
    } catch (error: any) {
      const isForceLogin = error.response?.status === 409 && 
        (error.response?.data?.code === 'FORCE_LOGIN_REQUIRED' || error.response?.data?.detail?.code === 'FORCE_LOGIN_REQUIRED');
      
      if (isForceLogin) {
        const message = error.response?.data?.detail?.message || error.response?.data?.message || 'This account is active on another device.';
        return { success: false, forceLoginRequired: true, message };
      }
      toast.error(error.response?.data?.detail || 'Login failed');
      return { success: false };
    }
  };

  const forceLogin = async (credentials: any) => {
    try {
      const response = await api.post('/auth/force-login', credentials);
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      setUser(response.data.user);
      toast.success('Logged in successfully');
      return { success: true, user: response.data.user };
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Force login failed');
      return { success: false };
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      window.location.href = '/login';
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, forceLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
