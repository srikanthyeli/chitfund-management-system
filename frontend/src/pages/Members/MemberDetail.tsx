import React, { useState, useEffect } from 'react';
import { ArrowLeft, User, Phone, MapPin, Edit, FileText } from 'lucide-react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import clsx from 'clsx';
import api from '../../core/api';
import toast from 'react-hot-toast';

import { ChangeMobileDialog } from './ChangeMobileDialog';
import { StatusDialog } from './StatusDialog';
import { useTranslation } from 'react-i18next';

interface MemberDetails {
  id: string;
  member_code: string;
  full_name: string;
  mobile: string;
  alternate_mobile: string | null;
  email: string | null;
  address: string | null;
  village: string | null;
  mandal: string | null;
  district: string | null;
  state: string | null;
  pincode: string | null;
  aadhaar_last4: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
}

interface ActivityLog {
  id: string;
  action_type: string;
  old_values: any;
  new_values: any;
  remarks: string | null;
  performed_by_name: string;
  created_at: string;
}

export const MemberDetail: React.FC = () => {
  const { t } = useTranslation(['members', 'collections', 'organisers', 'auth']);

  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [member, setMember] = useState<MemberDetails | null>(null);
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'chits' | 'history'>('overview');
  
  // Dialog States
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isStatusOpen, setIsStatusOpen] = useState(false);

  const fetchMemberDetails = async () => {
    try {
      const response = await api.get(`/members/${id}`);
      setMember(response.data);
    } catch (error) {
      toast.error('Failed to load member profile');
      navigate('/organizer/members');
    }
  };

  const fetchMemberActivity = async () => {
    try {
      const response = await api.get(`/members/${id}/activity`);
      setActivities(response.data);
    } catch (error) {
      console.error('Failed to load activity logs', error);
    }
  };

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([fetchMemberDetails(), fetchMemberActivity()]);
      setLoading(false);
    };
    loadAll();
  }, [id]);

  if (loading) {
    return <div className="flex justify-center p-8">Loading member profile...</div>;
  }

  if (!member) return null;

  const initials = member.full_name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const handleUpdateSuccess = (updated: MemberDetails) => {
    setMember(updated);
    fetchMemberActivity(); // Refresh activity log
  };

  return (
    <div className="max-w-3xl mx-auto h-full flex flex-col -mx-4 md:-mx-8 -mt-4 md:-mt-8 pb-10">
      
      {/* PhonePe-style Header */}
      <div className="bg-primary text-white p-4 pt-6 md:p-6 sticky top-0 z-10 shadow-md">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Link to="/organizer/members" className="p-1 hover:bg-white/10 rounded-full transition-colors">
              <ArrowLeft size={24} />
            </Link>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-xl font-bold">
                {initials}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-xl font-bold leading-tight">{member.full_name}</h1>
                  <span className={clsx(
                    "text-[10px] px-2 py-0.5 rounded-full font-bold",
                    member.is_active ? "bg-green-500 text-white" : "bg-rose-500 text-white"
                  )}>
                    {member.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <p className="text-primary-100 text-sm opacity-90">{member.member_code} • {member.mobile}</p>
              </div>
            </div>
          </div>

          <div className="flex space-x-2">
            <Link
              to={`/organizer/members/${member.id}/edit`}
              className="p-2 hover:bg-white/10 rounded-xl transition-colors border border-white/20 flex items-center space-x-1"
              title={t('members:members_edit')}
            >
              <Edit size={16} />
              <span className="hidden sm:inline text-xs font-semibold">{t('collections:collections_edit_button')}</span>
            </Link>
          </div>
        </div>

        {/* Action Buttons Row */}
        <div className="flex space-x-3 mb-4 px-1">
          <button
            onClick={() => setIsMobileOpen(true)}
            className="flex-1 sm:flex-initial bg-white/10 hover:bg-white/20 border border-white/10 rounded-xl py-2 px-4 text-xs font-bold text-white transition-all text-center"
          >
            Change Mobile
          </button>
          <button
            onClick={() => setIsStatusOpen(true)}
            className={clsx(
              "flex-1 sm:flex-initial rounded-xl py-2 px-4 text-xs font-bold transition-all text-center text-white border",
              member.is_active 
                ? "bg-rose-500/20 hover:bg-rose-500/35 border-rose-500/30" 
                : "bg-green-500/20 hover:bg-green-500/35 border-green-500/30"
            )}
          >
            {member.is_active ? 'Deactivate Member' : 'Activate Member'}
          </button>
        </div>

        {/* Tabs */}
        <div className="flex space-x-6 px-2 overflow-x-auto no-scrollbar">
          {(['overview', 'chits', 'history'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={clsx(
                "pb-3 text-sm font-medium transition-all whitespace-nowrap border-b-2",
                activeTab === tab 
                  ? "border-white text-white" 
                  : "border-transparent text-white/70 hover:text-white/90"
              )}
            >
              {tab === 'overview' ? 'Overview' : tab === 'chits' ? 'Chit Groups' : 'Activity Logs'}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 bg-slate-50 dark:bg-gray-900 p-4 md:p-6 overflow-y-auto">
        {activeTab === 'overview' && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-slate-100 dark:border-gray-700 p-5 space-y-5">
            <h2 className="text-base font-bold text-slate-800 dark:text-white border-b border-slate-100 dark:border-gray-700 pb-2">
              Profile details
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <User className="text-slate-400 mt-0.5" size={18} />
                <div>
                  <p className="text-xs text-slate-500">Full Name</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">{member.full_name}</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <FileText className="text-slate-400 mt-0.5" size={18} />
                <div>
                  <p className="text-xs text-slate-500">Member Code</p>
                  <p className="font-mono font-bold text-slate-800 dark:text-gray-200">{member.member_code}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <Phone className="text-slate-400 mt-0.5" size={18} />
                <div>
                  <p className="text-xs text-slate-500">Primary Mobile</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">{member.mobile}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Phone className="text-slate-400 mt-0.5" size={18} />
                <div>
                  <p className="text-xs text-slate-500">Alternate Mobile</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">{member.alternate_mobile || '-'}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <FileText className="text-slate-400 mt-0.5" size={18} />
                <div>
                  <p className="text-xs text-slate-500">Aadhaar (Last 4)</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">{member.aadhaar_last4 ? `xxxx xxxx ${member.aadhaar_last4}` : '-'}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <User className="text-slate-400 mt-0.5" size={18} />
                <div>
                  <p className="text-xs text-slate-500">{t('auth:login_email')}</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">{member.email || '-'}</p>
                </div>
              </div>
            </div>

            <div className="flex items-start space-x-3 border-t border-slate-50 dark:border-gray-700/50 pt-4">
              <MapPin className="text-slate-400 mt-0.5" size={18} />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
                <div>
                  <p className="text-xs text-slate-500">{t('organisers:organisers_address')}</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">{member.address || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Village / Mandal</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">
                    {member.village || '-'}{member.mandal ? `, ${member.mandal}` : ''}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">District / State</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">
                    {member.district || '-'}{member.state ? `, ${member.state}` : ''}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Pincode</p>
                  <p className="font-medium text-slate-800 dark:text-gray-200">{member.pincode || '-'}</p>
                </div>
              </div>
            </div>

            {member.notes && (
              <div className="border-t border-slate-50 dark:border-gray-700/50 pt-4">
                <p className="text-xs text-slate-500">Remarks / Notes</p>
                <p className="font-medium text-slate-700 dark:text-gray-300 mt-1 bg-slate-50 dark:bg-gray-900 p-3 rounded-xl border border-slate-100 dark:border-gray-800 text-sm">
                  {member.notes}
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'chits' && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-slate-100 dark:border-gray-700 p-6 text-center">
            <FileText className="mx-auto text-slate-300 dark:text-gray-600 mb-3" size={40} />
            <h3 className="font-bold text-slate-800 dark:text-white">No Chit Groups</h3>
            <p className="text-slate-500 text-xs mt-1 max-w-xs mx-auto">
              This member is not enrolled in any chit groups. Chit allocations and group operations will be implemented in the next phase.
            </p>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-slate-600 dark:text-gray-400 uppercase tracking-wider mb-2 pl-1">
              Audit Timeline
            </h3>

            {activities.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-slate-100 dark:border-gray-700 text-center">
                <p className="text-slate-500 text-xs">No activity logs recorded yet.</p>
              </div>
            ) : (
              <div className="relative pl-6 border-l-2 border-slate-200 dark:border-gray-700 space-y-6 py-2 ml-3">
                {activities.map((act) => (
                  <div key={act.id} className="relative">
                    {/* Timeline bullet dot */}
                    <span className={clsx(
                      "absolute -left-[31px] top-1.5 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800 flex items-center justify-center",
                      act.action_type === 'MEMBER_CREATED' ? "bg-green-500" :
                      act.action_type === 'MEMBER_DEACTIVATED' ? "bg-rose-500" :
                      act.action_type === 'MEMBER_ACTIVATED' ? "bg-green-500" :
                      "bg-primary"
                    )} />

                    <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-slate-100 dark:border-gray-700 shadow-sm space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                        <span className="font-bold text-slate-800 dark:text-white text-[14px]">
                          {act.action_type === 'MEMBER_CREATED' ? 'Member Registered' :
                           act.action_type === 'MEMBER_UPDATED' ? 'Profile Updated' :
                           act.action_type === 'MEMBER_MOBILE_UPDATED' ? 'Mobile Number Changed' :
                           act.action_type === 'MEMBER_ACTIVATED' ? 'Member Activated' :
                           act.action_type === 'MEMBER_DEACTIVATED' ? 'Member Deactivated' :
                           act.action_type}
                        </span>
                        <span className="text-[11px] text-slate-400 font-medium">
                          {new Date(act.created_at).toLocaleString('en-IN')}
                        </span>
                      </div>

                      <p className="text-xs text-slate-500">
                        Performed by: <span className="font-semibold text-slate-600 dark:text-gray-300">{act.performed_by_name}</span>
                      </p>

                      {/* Display Change Details */}
                      {act.action_type === 'MEMBER_UPDATED' && act.new_values && (
                        <div className="bg-slate-50 dark:bg-gray-900/50 p-2.5 rounded-lg border border-slate-100 dark:border-gray-850 text-xs space-y-1 mt-2">
                          <p className="font-semibold text-slate-500">Changed fields:</p>
                          {Object.keys(act.new_values).map((key) => (
                            <div key={key} className="grid grid-cols-3 gap-2 py-0.5">
                              <span className="font-mono text-slate-400 capitalize">{key.replace('_', ' ')}</span>
                              <span className="text-rose-500 line-through truncate">{String(act.old_values?.[key] || '-')}</span>
                              <span className="text-green-600 font-medium truncate">{String(act.new_values[key] || '-')}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {act.action_type === 'MEMBER_MOBILE_UPDATED' && act.new_values && (
                        <div className="bg-slate-50 dark:bg-gray-900/50 p-2 rounded-lg border border-slate-100 dark:border-gray-850 text-xs flex items-center space-x-2 mt-1">
                          <span className="text-rose-500 line-through">{act.old_values?.mobile}</span>
                          <span className="text-slate-400">→</span>
                          <span className="text-green-600 font-bold">{act.new_values?.mobile}</span>
                        </div>
                      )}

                      {act.remarks && (
                        <p className="text-[11px] text-slate-500 italic mt-1.5 bg-slate-50 dark:bg-gray-900 p-2 rounded-lg border border-slate-100 dark:border-gray-800">
                          Remarks: {act.remarks}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal Dialogs */}
      <ChangeMobileDialog
        isOpen={isMobileOpen}
        onClose={() => setIsMobileOpen(false)}
        memberId={member.id}
        currentMobile={member.mobile}
        onSuccess={handleUpdateSuccess}
      />

      <StatusDialog
        isOpen={isStatusOpen}
        onClose={() => setIsStatusOpen(false)}
        memberId={member.id}
        currentStatus={member.is_active}
        memberName={member.full_name}
        onSuccess={handleUpdateSuccess}
      />
    </div>
  );
};
