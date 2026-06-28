import React, { useEffect, useState } from 'react';
import { memberPortalApi } from '../api/memberPortalApi';
import type { NotificationResponse } from '../api/memberPortalApi';
import { Bell } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const MemberNotificationsPage: React.FC = () => {
  const { t } = useTranslation(['common']);

  const [notifications, setNotifications] = useState<NotificationResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotifs = async () => {
      try {
        const response = await memberPortalApi.getNotifications();
        setNotifications(response.items);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchNotifs();
  }, []);

  return (
    <div className="p-4 sm:p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold flex items-center"><Bell className="mr-2 text-purple-600"/>{t('common:navigation_notifications')}</h1>
      {loading ? <p>{t('common:loading')}</p> : (
        <div className="space-y-4">
          {notifications.length === 0 ? <p>No notifications.</p> : notifications.map(n => (
            <div key={n.id} className={`p-4 rounded-xl border ${n.is_read ? 'bg-white border-gray-200' : 'bg-purple-50 border-purple-200'}`}>
              <h3 className="font-bold">{n.title}</h3>
              <p className="text-sm text-gray-600">{n.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
