import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../core/api'; // uses axios with interceptors, but we might need to handle token injection separately or interceptors might need to check which token to use.
import toast from 'react-hot-toast';

interface MemberUser {
  id: string;
  mobile: string;
  role: string;
  organizer_id: string;
  name: string;
  member_code: string;
}

interface MemberAuthState {
  user: MemberUser | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (mobile: string, password: string) => Promise<boolean>;
  logout: () => void;
  setToken: (token: string) => void;
}

export const useMemberAuthStore = create<MemberAuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: async (mobile: string, password: string) => {
        try {
          const response = await api.post('/member/auth/login', { mobile, password });
          set({
            user: response.data.user,
            token: response.data.access_token,
            isAuthenticated: true,
          });
          return true;
        } catch (error: any) {
          toast.error(error.response?.data?.message || 'Login failed');
          return false;
        }
      },
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
      setToken: (token: string) => set({ token }),
    }),
    {
      name: 'member-auth-storage', // unique name
    }
  )
);
