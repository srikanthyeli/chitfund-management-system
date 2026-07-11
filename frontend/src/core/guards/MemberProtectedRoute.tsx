import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useMemberAuthStore } from '../../store/memberAuthStore';
import { useTranslation } from 'react-i18next';

export const MemberProtectedRoute: React.FC = () => {
  const { t } = useTranslation(['common']);
  const { user, isAuthenticated } = useMemberAuthStore();

  if (!isAuthenticated || !user) {
    return <Navigate to="/member/login" replace />;
  }

  return <Outlet />;
};
