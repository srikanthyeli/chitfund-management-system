import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Edit, UserPlus, Play, CheckCircle2, 
  XCircle, RotateCcw, AlertTriangle, Calendar, User, 
  MapPin, Phone, RefreshCw, BookOpen, Gavel, Activity
} from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';
import clsx from 'clsx';

interface MembershipItem {
  membership_id: string;
  member_id: string;
  member_code: string;
  full_name: string;
  mobile: string;
  village: string | null;
  share_count: number;
  membership_status: string;
}

interface ChitGroupDetail {
  id: string;
  organizer_id: string;
  chit_code: string;
  chit_name: string;
  description: string | null;
  total_chit_value: number;
  monthly_installment_per_share: number;
  total_shares: number;
  duration_months: number;
  maintenance_charge: number;
  maintenance_charge_type: 'FIXED' | 'PERCENTAGE';
  start_date: string;
  installment_due_day: number;
  status: 'DRAFT' | 'READY_TO_START' | 'ACTIVE' | 'CANCELLED';
  allocated_shares: number;
  available_shares: number;
  member_count: number;
  monthly_pool: number;
  memberships: MembershipItem[];
  created_at: string;
  updated_at: string | null;
}

interface AvailableMember {
  id: string;
  member_code: string;
  full_name: string;
  mobile: string;
  village: string | null;
  is_active: boolean;
  existing_shares: number;
}

interface ActivityLogItem {
  id: string;
  action_type: string;
  old_values: any | null;
  new_values: any | null;
  remarks: string | null;
  performed_by_user_id: string | null;
  created_at: string;
}

export const ChitGroupDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [chit, setChit] = useState<ChitGroupDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'members' | 'activity'>('members');
  const [activities, setActivities] = useState<ActivityLogItem[]>([]);
  const [loadingActivities, setLoadingActivities] = useState(false);

  // Available members list for dropdown
  const [availableMembers, setAvailableMembers] = useState<AvailableMember[]>([]);

  // Modals state
  const [isAllocateOpen, setIsAllocateOpen] = useState(false);
  const [allocSearch, setAllocSearch] = useState('');
  const [allocSelectedIds, setAllocSelectedIds] = useState<string[]>([]);
  const [allocSharesPerMember, setAllocSharesPerMember] = useState<number>(1);
  const [allocRemarks, setAllocRemarks] = useState('');
  const [submittingAlloc, setSubmittingAlloc] = useState(false);

  const [isEditSharesOpen, setIsEditSharesOpen] = useState(false);
  const [selectedMembership, setSelectedMembership] = useState<MembershipItem | null>(null);
  const [editShareCount, setEditShareCount] = useState(1);
  const [editRemarks, setEditRemarks] = useState('');
  const [submittingEditShares, setSubmittingEditShares] = useState(false);

  const [isRemoveMemberOpen, setIsRemoveMemberOpen] = useState(false);
  const [removeRemarks, setRemoveRemarks] = useState('');
  const [submittingRemove, setSubmittingRemove] = useState(false);

  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [targetStatus, setTargetStatus] = useState<'DRAFT' | 'READY_TO_START' | 'ACTIVE' | 'CANCELLED' | ''>('');
  const [statusRemarks, setStatusRemarks] = useState('');
  const [submittingStatus, setSubmittingStatus] = useState(false);

  const fetchChitDetails = async () => {
    try {
      const response = await api.get(`/chit-groups/${id}`);
      setChit(response.data);
    } catch (error) {
      toast.error('Failed to load chit group details');
      navigate('/organizer/chit-groups');
    } finally {
      setLoading(false);
    }
  };

  const fetchActivityLogs = async () => {
    setLoadingActivities(true);
    try {
      const response = await api.get(`/chit-groups/${id}/activity?page=1&page_size=50`);
      setActivities(response.data);
    } catch (error) {
      console.error('Failed to load activity logs');
    } finally {
      setLoadingActivities(false);
    }
  };

  const fetchAvailableMembers = async () => {
    try {
      const response = await api.get(`/chit-groups/${id}/available-members`);
      setAvailableMembers(response.data);
    } catch (error) {
      console.error('Failed to load available members list');
    }
  };

  useEffect(() => {
    fetchChitDetails();
  }, [id]);

  useEffect(() => {
    if (activeTab === 'activity') {
      fetchActivityLogs();
    }
  }, [activeTab, id]);

  const handleOpenAllocate = () => {
    fetchAvailableMembers();
    setAllocSearch('');
    setAllocSelectedIds([]);
    setAllocSharesPerMember(1);
    setAllocRemarks('');
    setIsAllocateOpen(true);
  };

  const handleAllocateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (allocSelectedIds.length === 0) {
      toast.error('Please select at least one member');
      return;
    }
    if (allocSharesPerMember < 1) {
      toast.error('Share count must be at least 1');
      return;
    }
    const totalToAdd = allocSelectedIds.length * allocSharesPerMember;
    if (chit && totalToAdd > chit.available_shares) {
      toast.error(`Only ${chit.available_shares} shares are available to allocate`);
      return;
    }

    // Show final confirmation
    const confirmMsg = `You are allocating ${allocSharesPerMember} shares each to ${allocSelectedIds.length} members. Total shares to add: ${totalToAdd}. Are you sure?`;
    if (!window.confirm(confirmMsg)) {
      return;
    }

    setSubmittingAlloc(true);
    try {
      await api.post(`/chit-groups/${id}/memberships/bulk-allocate`, {
        member_ids: allocSelectedIds,
        share_count_per_member: allocSharesPerMember,
        remarks: allocRemarks.trim() || null
      });
      toast.success('Shares allocated successfully!');
      setIsAllocateOpen(false);
      fetchChitDetails();
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to allocate shares');
    } finally {
      setSubmittingAlloc(false);
    }
  };

  const handleOpenEditShares = (m: MembershipItem) => {
    setSelectedMembership(m);
    setEditShareCount(m.share_count);
    setEditRemarks('');
    setIsEditSharesOpen(true);
  };

  const handleEditSharesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMembership) return;
    if (editShareCount < 1) {
      toast.error('Share count must be at least 1');
      return;
    }
    
    const diff = editShareCount - selectedMembership.share_count;
    if (chit && diff > 0 && diff > chit.available_shares) {
      toast.error(`Insufficient available shares. Only ${chit.available_shares} shares left.`);
      return;
    }

    setSubmittingEditShares(true);
    try {
      await api.put(`/chit-groups/${id}/memberships/${selectedMembership.membership_id}`, {
        share_count: editShareCount,
        remarks: editRemarks.trim() || null
      });
      toast.success('Shares updated successfully!');
      setIsEditSharesOpen(false);
      fetchChitDetails();
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to update shares');
    } finally {
      setSubmittingEditShares(false);
    }
  };

  const handleOpenRemove = (m: MembershipItem) => {
    setSelectedMembership(m);
    setRemoveRemarks('');
    setIsRemoveMemberOpen(true);
  };

  const handleRemoveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMembership) return;

    setSubmittingRemove(true);
    try {
      await api.delete(`/chit-groups/${id}/memberships/${selectedMembership.membership_id}?remarks=${encodeURIComponent(removeRemarks.trim())}`);
      toast.success('Member removed from chit group');
      setIsRemoveMemberOpen(false);
      fetchChitDetails();
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to remove member');
    } finally {
      setSubmittingRemove(false);
    }
  };

  const handleOpenStatusChange = (status: 'DRAFT' | 'READY_TO_START' | 'ACTIVE' | 'CANCELLED') => {
    setTargetStatus(status);
    setStatusRemarks('');
    setIsStatusModalOpen(true);
  };

  const handleStatusSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetStatus) return;

    if (targetStatus === 'CANCELLED' && !statusRemarks.trim()) {
      toast.error('Remarks are required to cancel a chit group');
      return;
    }

    setSubmittingStatus(true);
    try {
      await api.post(`/chit-groups/${id}/status`, {
        status: targetStatus,
        remarks: statusRemarks.trim() || null
      });
      toast.success(`Chit group status updated to ${targetStatus.replace(/_/g, ' ')}`);
      setIsStatusModalOpen(false);
      fetchChitDetails();
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to update status');
    } finally {
      setSubmittingStatus(false);
    }
  };

  const filteredMembers = availableMembers.filter(m => {
    const query = allocSearch.toLowerCase();
    return (
      m.full_name.toLowerCase().includes(query) ||
      m.mobile.includes(query) ||
      m.member_code.toLowerCase().includes(query) ||
      (m.village && m.village.toLowerCase().includes(query))
    );
  });

  const totalSharesToAdd = allocSelectedIds.length * allocSharesPerMember;
  const availableSharesLeft = chit ? chit.available_shares : 0;
  const remainingAfterAlloc = availableSharesLeft - totalSharesToAdd;
  const exceedsAvailable = totalSharesToAdd > availableSharesLeft;

  if (loading) {
    return <div className="text-center py-12 text-slate-500">Loading chit group details...</div>;
  }

  if (!chit) {
    return <div className="text-center py-12 text-red-500">Chit group not found.</div>;
  }

  const isDraft = chit.status === 'DRAFT';
  const isReady = chit.status === 'READY_TO_START';
  const isActive = chit.status === 'ACTIVE';
  const isCancelled = chit.status === 'CANCELLED';

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'DRAFT': return 'Draft (Allocating Shares)';
      case 'READY_TO_START': return 'Ready To Start';
      case 'ACTIVE': return 'Active (Running)';
      case 'CANCELLED': return 'Cancelled';
      default: return status;
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto p-1 sm:p-4 pb-20">
      
      {/* Back button & title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <Link to="/organizer/chit-groups" className="p-2 hover:bg-slate-100 dark:hover:bg-gray-800 rounded-full transition-colors text-slate-600 dark:text-slate-400">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-slate-800 dark:text-white">{chit.chit_name}</h1>
              <span className="font-mono text-xs bg-slate-100 dark:bg-gray-800 px-2 py-0.5 rounded text-slate-500 font-bold">{chit.chit_code}</span>
            </div>
            <p className="text-sm text-slate-500 mt-0.5">
              ₹{Number(chit.monthly_installment_per_share).toLocaleString('en-IN')}/mo per share • {chit.total_shares} total shares
            </p>
          </div>
        </div>

        {/* Action Status buttons */}
        <div className="flex flex-wrap gap-2">
          {isDraft && (
            <>
              <Link
                to={`/organizer/chit-groups/${chit.id}/edit`}
                className="inline-flex items-center space-x-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-gray-750 dark:hover:bg-gray-700 text-slate-700 dark:text-gray-300 px-4 py-2 rounded-xl text-sm font-semibold transition-colors"
              >
                <Edit size={16} />
                <span>Edit Settings</span>
              </Link>
              {chit.allocated_shares === chit.total_shares && (
                <button
                  onClick={() => handleOpenStatusChange('READY_TO_START')}
                  className="inline-flex items-center space-x-1.5 bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-xl text-sm font-semibold transition-colors shadow-sm"
                >
                  <CheckCircle2 size={16} />
                  <span>Mark Ready to Start</span>
                </button>
              )}
              <button
                onClick={() => handleOpenStatusChange('CANCELLED')}
                className="inline-flex items-center space-x-1.5 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/20 dark:hover:bg-rose-900/20 text-rose-700 dark:text-rose-400 px-4 py-2 rounded-xl text-sm font-semibold transition-colors"
              >
                <XCircle size={16} />
                <span>Cancel Group</span>
              </button>
            </>
          )}

          {isReady && (
            <>
              <button
                onClick={() => handleOpenStatusChange('DRAFT')}
                className="inline-flex items-center space-x-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-gray-750 dark:hover:bg-gray-700 text-slate-700 dark:text-gray-300 px-4 py-2 rounded-xl text-sm font-semibold transition-colors"
              >
                <RotateCcw size={16} />
                <span>Revert to Draft</span>
              </button>
              <button
                onClick={() => handleOpenStatusChange('ACTIVE')}
                className="inline-flex items-center space-x-1.5 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-colors shadow-sm"
              >
                <Play size={16} />
                <span>Activate Chit Group</span>
              </button>
              <button
                onClick={() => handleOpenStatusChange('CANCELLED')}
                className="inline-flex items-center space-x-1.5 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/20 dark:hover:bg-rose-900/20 text-rose-700 dark:text-rose-400 px-4 py-2 rounded-xl text-sm font-semibold transition-colors"
              >
                <XCircle size={16} />
                <span>Cancel Group</span>
              </button>
            </>
          )}

          {isActive && (
            <div className="flex items-center gap-3 flex-wrap">
              <div className="bg-green-50 dark:bg-green-950/25 border border-green-200 dark:border-green-800/40 text-green-700 dark:text-green-400 px-4 py-2 rounded-xl text-sm font-bold flex items-center space-x-2">
                <CheckCircle2 size={16} />
                <span>Chit is Active (Financials Locked)</span>
              </div>
              <Link
                to={`/organizer/chit-groups/${chit.id}/auctions`}
                className="inline-flex items-center space-x-2 bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-colors shadow-sm"
              >
                <Gavel size={16} />
                <span>Monthly Auctions</span>
              </Link>

              <Link 
                to={`/organizer/chit-groups/${chit.id}/financial-summary`}
                className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex items-center gap-3 hover:border-purple-300 transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 shrink-0">
                  <Activity size={20} />
                </div>
                <div className="flex flex-col font-medium text-gray-900 dark:text-gray-100">
                  <span>Financial Summary</span>
                  <span className="text-xs text-gray-500 font-normal mt-0.5">View payouts and closures</span>
                </div>
              </Link>
            </div>
          )}

          {isCancelled && (
            <div className="bg-rose-50 dark:bg-rose-950/25 border border-rose-200 dark:border-rose-800/40 text-rose-700 dark:text-rose-400 px-4 py-2 rounded-xl text-sm font-bold flex items-center space-x-2">
              <XCircle size={16} />
              <span>Chit Cancelled</span>
            </div>
          )}
        </div>
      </div>

      {/* Grid of Key Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Card: Financial Stats */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider border-b pb-2">Financial Config</h3>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Chit Value</span>
              <span className="font-bold text-slate-800 dark:text-white">₹{Number(chit.total_chit_value).toLocaleString('en-IN')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Installment per Share</span>
              <span className="font-semibold text-slate-800 dark:text-white">₹{Number(chit.monthly_installment_per_share).toLocaleString('en-IN')}/mo</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Total Shares / Duration</span>
              <span className="font-semibold text-slate-800 dark:text-white">{chit.total_shares} Shares ({chit.duration_months} Months)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Monthly Pool Amount</span>
              <span className="font-bold text-primary">₹{Number(chit.monthly_pool).toLocaleString('en-IN')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Organizer Fee</span>
              <span className="font-semibold text-slate-800 dark:text-white">
                {chit.maintenance_charge_type === 'FIXED' ? '₹' : ''}
                {chit.maintenance_charge}
                {chit.maintenance_charge_type === 'PERCENTAGE' ? '%' : ''}
              </span>
            </div>
            <div className="flex justify-between border-t pt-2.5">
              <span className="text-slate-500">Start Date</span>
              <span className="font-semibold text-slate-800 dark:text-white">
                {new Date(chit.start_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Installment Due Day</span>
              <span className="font-semibold text-slate-800 dark:text-white">Day {chit.installment_due_day} of Month</span>
            </div>
          </div>
        </div>

        {/* Middle Card: Share Allocation Status */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider border-b pb-2">Allocation Progress</h3>
            
            <div className="mt-4 space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Allocated Shares</span>
                <span className="font-bold text-slate-800 dark:text-white">{chit.allocated_shares} / {chit.total_shares}</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-gray-700 h-3 rounded-full overflow-hidden">
                <div 
                  className="bg-primary h-full rounded-full transition-all duration-500" 
                  style={{ width: `${(chit.allocated_shares / chit.total_shares) * 100}%` }}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-center mt-2">
                <div className="bg-slate-50 dark:bg-gray-900 p-2.5 rounded-xl">
                  <p className="text-[10px] font-semibold text-slate-400 uppercase">Available</p>
                  <p className="text-lg font-bold text-slate-800 dark:text-white">{chit.available_shares}</p>
                </div>
                <div className="bg-slate-50 dark:bg-gray-900 p-2.5 rounded-xl">
                  <p className="text-[10px] font-semibold text-slate-400 uppercase">Members</p>
                  <p className="text-lg font-bold text-slate-800 dark:text-white">{chit.member_count}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="text-xs text-slate-400 mt-4 flex items-start space-x-1">
            <Calendar size={14} className="shrink-0 mt-0.5" />
            <span>
              {isDraft && chit.available_shares > 0 && `Requires ${chit.available_shares} more shares allocated to mark Ready to Start.`}
              {isDraft && chit.available_shares === 0 && 'Ready to start. Please click "Mark Ready to Start" above.'}
              {!isDraft && `Status is ${getStatusLabel(chit.status)}.`}
            </span>
          </div>
        </div>

        {/* Right Card: Group Description / Notes */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider border-b pb-2">Status & Description</h3>
          
          <div className="space-y-4">
            <div>
              <p className="text-xs text-slate-400">Current Status</p>
              <div className="mt-1">
                <span className={clsx(
                  "inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider",
                  getStatusBadge(chit.status)
                )}>
                  {chit.status.replace(/_/g, ' ')}
                </span>
              </div>
            </div>

            <div>
              <p className="text-xs text-slate-400">Notes / Terms</p>
              <p className="text-sm text-slate-600 dark:text-gray-300 mt-1 italic whitespace-pre-line leading-relaxed">
                {chit.description || 'No special terms or notes provided for this chit group.'}
              </p>
            </div>
          </div>
        </div>

      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('members')}
          className={clsx(
            "py-3 px-6 text-sm font-semibold uppercase tracking-wider border-b-2 transition-colors",
            activeTab === 'members'
              ? "border-primary text-primary"
              : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-white"
          )}
        >
          Allocated Members ({chit.member_count})
        </button>
        <button
          onClick={() => setActiveTab('activity')}
          className={clsx(
            "py-3 px-6 text-sm font-semibold uppercase tracking-wider border-b-2 transition-colors",
            activeTab === 'activity'
              ? "border-primary text-primary"
              : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-white"
          )}
        >
          Activity Logs
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'members' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">Allocated Share Members</h3>
            {isDraft && chit.available_shares > 0 && (
              <button
                onClick={handleOpenAllocate}
                className="inline-flex items-center space-x-1.5 bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-xl text-xs font-semibold transition-colors shadow-sm"
              >
                <UserPlus size={14} />
                <span>Allocate Shares</span>
              </button>
            )}
          </div>

          {/* Members Table */}
          {chit.memberships.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 text-center py-12 rounded-2xl border border-slate-100 dark:border-gray-700">
              <User className="mx-auto text-slate-300 dark:text-gray-650 mb-3" size={40} />
              <h4 className="text-sm font-bold text-slate-700 dark:text-white">No Members Allocated</h4>
              <p className="text-slate-400 text-xs mt-0.5">Start allocating member shares to populate this group.</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-slate-100 dark:border-gray-700 overflow-hidden shadow-sm">
              
              {/* Desktop view */}
              <div className="hidden sm:block">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 dark:bg-gray-850 text-slate-500 dark:text-gray-400 font-semibold text-xs uppercase tracking-wider border-b border-slate-100 dark:border-gray-700">
                      <th className="px-6 py-3">Code</th>
                      <th className="px-6 py-3">Member Name</th>
                      <th className="px-6 py-3">Contact</th>
                      <th className="px-6 py-3">Village</th>
                      <th className="px-6 py-3 text-center">Allocated Shares</th>
                      {isDraft && <th className="px-6 py-3 text-right">Actions</th>}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-gray-700 text-sm text-slate-700 dark:text-gray-300">
                    {chit.memberships.map((m) => (
                      <tr key={m.membership_id} className="hover:bg-slate-50 dark:hover:bg-gray-750/50">
                        <td className="px-6 py-3.5 font-mono text-xs font-bold text-slate-500">{m.member_code}</td>
                        <td className="px-6 py-3.5 font-bold text-slate-800 dark:text-white">{m.full_name}</td>
                        <td className="px-6 py-3.5">{m.mobile}</td>
                        <td className="px-6 py-3.5">{m.village || '-'}</td>
                        <td className="px-6 py-3.5 text-center font-bold text-slate-800 dark:text-white">{m.share_count}</td>
                        {isDraft && (
                          <td className="px-6 py-3.5 text-right space-x-2">
                            <button
                              onClick={() => handleOpenEditShares(m)}
                              className="text-primary hover:text-primary-dark font-medium text-xs bg-purple-50 dark:bg-purple-950/20 px-2.5 py-1 rounded-lg"
                            >
                              Edit Shares
                            </button>
                            <button
                              onClick={() => handleOpenRemove(m)}
                              className="text-rose-600 hover:text-rose-800 font-medium text-xs bg-rose-50 dark:bg-rose-955/20 px-2.5 py-1 rounded-lg"
                            >
                              Remove
                            </button>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile View */}
              <div className="block sm:hidden divide-y divide-slate-100 dark:divide-gray-700">
                {chit.memberships.map((m) => (
                  <div key={m.membership_id} className="p-4 space-y-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-slate-800 dark:text-white">{m.full_name}</h4>
                        <span className="font-mono text-xs text-slate-400">{m.member_code}</span>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-slate-400">Shares</span>
                        <p className="font-bold text-base text-slate-800 dark:text-white">{m.share_count}</p>
                      </div>
                    </div>

                    <div className="flex flex-col gap-0.5 text-xs text-slate-500">
                      <div className="flex items-center space-x-1"><Phone size={12} /> <span>{m.mobile}</span></div>
                      {m.village && <div className="flex items-center space-x-1"><MapPin size={12} /> <span>{m.village}</span></div>}
                    </div>

                    {isDraft && (
                      <div className="flex space-x-2 pt-2">
                        <button
                          onClick={() => handleOpenEditShares(m)}
                          className="flex-1 text-center py-2 bg-slate-100 hover:bg-slate-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-slate-700 dark:text-gray-300 rounded-lg text-xs font-semibold"
                        >
                          Edit Shares
                        </button>
                        <button
                          onClick={() => handleOpenRemove(m)}
                          className="flex-1 text-center py-2 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/20 text-rose-700 dark:text-rose-400 rounded-lg text-xs font-semibold"
                        >
                          Remove Member
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>

            </div>
          )}
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-bold text-slate-800 dark:text-white font-serif">Audit Activity Log</h3>
            <button 
              onClick={fetchActivityLogs}
              className="p-2 hover:bg-slate-100 dark:hover:bg-gray-800 rounded-lg text-slate-600 dark:text-slate-400 transition-colors"
            >
              <RefreshCw size={16} className={clsx(loadingActivities && "animate-spin")} />
            </button>
          </div>

          {loadingActivities ? (
            <div className="text-center py-12 text-slate-500">Loading audit history...</div>
          ) : activities.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 text-center py-12 rounded-2xl border border-slate-100 dark:border-gray-700">
              <BookOpen className="mx-auto text-slate-300 dark:text-gray-650 mb-3" size={40} />
              <h4 className="text-sm font-bold text-slate-700 dark:text-white">No Activity Logs</h4>
              <p className="text-slate-400 text-xs mt-0.5">Activity statements will appear here as updates occur.</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm p-4 space-y-4 max-h-[500px] overflow-y-auto">
              <div className="relative border-l-2 border-slate-150 dark:border-gray-700 ml-3 pl-6 space-y-6 py-2">
                {activities.map((act) => (
                  <div key={act.id} className="relative">
                    {/* Circle marker */}
                    <span className="absolute -left-[31px] top-1.5 w-3 h-3 rounded-full bg-primary ring-4 ring-white dark:ring-gray-850" />
                    
                    <div className="space-y-1">
                      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1">
                        <span className="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider">{act.action_type.replace(/_/g, ' ')}</span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {new Date(act.created_at).toLocaleString('en-IN')}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-gray-300 leading-relaxed font-semibold">{act.remarks}</p>
                      
                      {/* JSON Differences visualizer */}
                      {(act.old_values || act.new_values) && (
                        <div className="bg-slate-50 dark:bg-gray-900 p-2 rounded-xl text-[10px] font-mono mt-1 max-w-lg space-y-0.5 text-slate-500 overflow-x-auto">
                          {Object.keys(act.new_values || act.old_values || {}).map((key) => (
                            <div key={key} className="flex flex-wrap">
                              <span className="font-bold text-slate-600 dark:text-gray-400 mr-2">{key}:</span>
                              {act.old_values && act.old_values[key] !== undefined && (
                                <span className="line-through text-rose-500 mr-1.5">{String(act.old_values[key])}</span>
                              )}
                              {act.new_values && act.new_values[key] !== undefined && (
                                <span className="text-green-600 font-bold">{String(act.new_values[key])}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* MODAL 1: Allocate Member Shares */}
      {isAllocateOpen && chit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full border border-slate-100 dark:border-gray-700 shadow-xl overflow-hidden">
            <div className="p-5 border-b border-slate-100 dark:border-gray-700">
              <h3 className="text-base font-bold text-slate-800 dark:text-white">Allocate Shares to Members</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Select active members and specify equal shares to allocate.
              </p>
            </div>
            
            <form onSubmit={handleAllocateSubmit} className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                  Search & Select Members <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="Search by name, phone, code..."
                  value={allocSearch}
                  onChange={(e) => setAllocSearch(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm mb-2"
                />
                
                <div className="flex justify-between items-center mb-2 px-1">
                  <span className="text-xs text-slate-500 font-semibold">
                    {filteredMembers.length} members found
                  </span>
                  {filteredMembers.length > 0 && (
                    <button
                      type="button"
                      onClick={() => {
                        const filteredIds = filteredMembers.map(m => m.id);
                        const allSelected = filteredIds.every(id => allocSelectedIds.includes(id));
                        if (allSelected) {
                          setAllocSelectedIds(prev => prev.filter(id => !filteredIds.includes(id)));
                        } else {
                          setAllocSelectedIds(prev => Array.from(new Set([...prev, ...filteredIds])));
                        }
                      }}
                      className="text-primary hover:text-primary-dark text-xs font-bold"
                    >
                      {filteredMembers.map(m => m.id).every(id => allocSelectedIds.includes(id)) ? 'Deselect All' : 'Select All'}
                    </button>
                  )}
                </div>

                <div className="border border-slate-200 dark:border-gray-700 rounded-xl overflow-hidden max-h-48 overflow-y-auto mb-4 bg-slate-50 dark:bg-gray-900/50">
                  {filteredMembers.length === 0 ? (
                    <div className="text-center py-6 text-slate-500 text-xs font-semibold">
                      No active members found.
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-150 dark:divide-gray-800">
                      {filteredMembers.map((m) => {
                        const isChecked = allocSelectedIds.includes(m.id);
                        return (
                          <label
                            key={m.id}
                            className="flex items-center space-x-3 p-3 hover:bg-slate-100 dark:hover:bg-gray-850 cursor-pointer select-none"
                          >
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => {
                                if (isChecked) {
                                  setAllocSelectedIds(prev => prev.filter(id => id !== m.id));
                                } else {
                                  setAllocSelectedIds(prev => [...prev, m.id]);
                                }
                              }}
                              className="rounded text-primary focus:ring-primary h-4 w-4"
                            />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-bold text-slate-800 dark:text-white truncate">
                                {m.full_name}
                              </p>
                              <p className="text-xs text-slate-500 dark:text-gray-400 font-semibold">
                                {m.member_code} • {m.mobile} {m.village ? `• ${m.village}` : ''}
                              </p>
                            </div>
                            {m.existing_shares > 0 && (
                              <span className="text-[10px] bg-purple-50 dark:bg-purple-950/40 text-primary dark:text-purple-300 font-bold px-2.5 py-0.5 rounded-full shrink-0">
                                {m.existing_shares} existing share(s)
                              </span>
                            )}
                          </label>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    Shares Per Member <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={allocSharesPerMember}
                    onChange={(e) => setAllocSharesPerMember(parseInt(e.target.value) || 1)}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    Remarks (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Bulk allocation"
                    value={allocRemarks}
                    onChange={(e) => setAllocRemarks(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm"
                  />
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-gray-900 p-4 rounded-xl space-y-2 text-xs">
                <h4 className="font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-[10px]">
                  Real-time Calculation
                </h4>
                <div className="grid grid-cols-2 gap-y-1.5 text-slate-600 dark:text-gray-300">
                  <div>Selected Members:</div>
                  <div className="text-right font-bold text-slate-800 dark:text-white">
                    {allocSelectedIds.length}
                  </div>
                  
                  <div>Shares Per Member:</div>
                  <div className="text-right font-bold text-slate-800 dark:text-white">
                    {allocSharesPerMember}
                  </div>
                  
                  <div className="border-t pt-1.5 font-semibold">Total Shares to Add:</div>
                  <div className={clsx("text-right border-t pt-1.5 font-bold", exceedsAvailable ? "text-rose-500 animate-pulse" : "text-slate-800 dark:text-white")}>
                    {totalSharesToAdd}
                  </div>
                  
                  <div>Available Shares:</div>
                  <div className="text-right font-bold text-slate-800 dark:text-white">
                    {availableSharesLeft}
                  </div>
                  
                  <div className="border-t pt-1.5 font-semibold">Remaining Shares:</div>
                  <div className={clsx("text-right border-t pt-1.5 font-bold", remainingAfterAlloc < 0 ? "text-rose-500" : "text-green-600 dark:text-green-400")}>
                    {remainingAfterAlloc}
                  </div>
                </div>
              </div>

              {allocSelectedIds.length > 0 && !exceedsAvailable && (
                <div className="bg-purple-50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-900/40 p-3 rounded-xl text-xs text-primary dark:text-purple-300 font-semibold leading-relaxed">
                  Confirm: You are allocating {allocSharesPerMember} shares each to {allocSelectedIds.length} members. Total shares to add: {totalSharesToAdd}.
                </div>
              )}

              <div className="flex space-x-3 pt-3 border-t border-slate-100 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => setIsAllocateOpen(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-slate-700 dark:text-gray-300 font-medium text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingAlloc || allocSelectedIds.length === 0 || exceedsAvailable || allocSharesPerMember <= 0 || chit.status !== 'DRAFT'}
                  className="flex-1 py-2.5 rounded-xl bg-primary hover:bg-primary-dark text-white font-medium text-xs font-semibold disabled:opacity-50"
                >
                  {submittingAlloc ? 'Allocating...' : 'Allocate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: Edit Share Count */}
      {isEditSharesOpen && selectedMembership && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full border border-slate-100 dark:border-gray-700 shadow-xl overflow-hidden">
            <div className="p-5 border-b border-slate-100 dark:border-gray-700">
              <h3 className="text-base font-bold text-slate-800 dark:text-white">Modify Member Shares</h3>
              <p className="text-xs text-slate-500 mt-0.5">Change share allocations for {selectedMembership.full_name}.</p>
            </div>
            
            <form onSubmit={handleEditSharesSubmit} className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Share Count <span className="text-rose-500">*</span></label>
                <input
                  type="number"
                  required
                  min="1"
                  value={editShareCount}
                  onChange={(e) => setEditShareCount(parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm"
                />
                <p className="text-[10px] text-slate-400 mt-1">
                  Current: {selectedMembership.share_count} • Max additional allocation limit: +{chit.available_shares} shares
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Reason for Change <span className="text-rose-500">*</span></label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Member requested higher share allocation"
                  value={editRemarks}
                  onChange={(e) => setEditRemarks(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm"
                />
              </div>

              <div className="flex space-x-3 pt-3 border-t border-slate-100 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => setIsEditSharesOpen(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-slate-700 dark:text-gray-300 font-medium text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingEditShares}
                  className="flex-1 py-2.5 rounded-xl bg-primary hover:bg-primary-dark text-white font-medium text-xs disabled:opacity-50"
                >
                  {submittingEditShares ? 'Updating...' : 'Update Shares'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: Remove Member */}
      {isRemoveMemberOpen && selectedMembership && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full border border-slate-100 dark:border-gray-700 shadow-xl overflow-hidden">
            <div className="p-5 border-b border-rose-100 dark:border-rose-900/30 bg-rose-50 dark:bg-rose-950/20 text-rose-800 dark:text-rose-400">
              <h3 className="text-base font-bold flex items-center space-x-2">
                <AlertTriangle size={18} />
                <span>Remove Member from Chit</span>
              </h3>
              <p className="text-xs mt-1">You are about to soft remove {selectedMembership.full_name} from this group.</p>
            </div>
            
            <form onSubmit={handleRemoveSubmit} className="p-5 space-y-4">
              <p className="text-xs text-slate-600 dark:text-gray-300 font-semibold">
                Removed shares ({selectedMembership.share_count} share(s)) will be returned back to the available pool.
              </p>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Reason for Removal <span className="text-rose-500">*</span></label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Switched to another scheme, opted out"
                  value={removeRemarks}
                  onChange={(e) => setRemoveRemarks(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm"
                />
              </div>

              <div className="flex space-x-3 pt-3 border-t border-slate-100 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => setIsRemoveMemberOpen(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-slate-700 dark:text-gray-300 font-medium text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingRemove}
                  className="flex-1 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-medium text-xs disabled:opacity-50"
                >
                  {submittingRemove ? 'Removing...' : 'Confirm Remove'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 4: Change Status Confirmation */}
      {isStatusModalOpen && targetStatus && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full border border-slate-100 dark:border-gray-700 shadow-xl overflow-hidden">
            <div className="p-5 border-b border-slate-100 dark:border-gray-700">
              <h3 className="text-base font-bold text-slate-800 dark:text-white">Confirm Status Transition</h3>
              <p className="text-xs text-slate-500 mt-0.5">Transition chit group status to {getStatusLabel(targetStatus)}.</p>
            </div>
            
            <form onSubmit={handleStatusSubmit} className="p-5 space-y-4">
              <p className="text-xs text-slate-600 dark:text-gray-300 leading-relaxed font-semibold">
                {targetStatus === 'READY_TO_START' && 'This marks the group as ready to start. Member allocation will be locked.'}
                {targetStatus === 'DRAFT' && 'Reverting to draft status allows you to edit settings and adjust member shares.'}
                {targetStatus === 'ACTIVE' && 'Activating the chit starts the monthly cycles. Financial parameters will be locked permanently.'}
                {targetStatus === 'CANCELLED' && 'Cancelling the chit terminates this group. This cannot be undone.'}
              </p>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                  Remarks / Notes {targetStatus === 'CANCELLED' && <span className="text-rose-500">*</span>}
                </label>
                <textarea
                  required={targetStatus === 'CANCELLED'}
                  rows={2}
                  placeholder={targetStatus === 'CANCELLED' ? "Provide reason for cancellation..." : "Optional comments..."}
                  value={statusRemarks}
                  onChange={(e) => setStatusRemarks(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm resize-none"
                />
              </div>

              <div className="flex space-x-3 pt-3 border-t border-slate-100 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => setIsStatusModalOpen(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-slate-700 dark:text-gray-300 font-medium text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingStatus}
                  className="flex-1 py-2.5 rounded-xl bg-primary hover:bg-primary-dark text-white font-medium text-xs disabled:opacity-50"
                >
                  {submittingStatus ? 'Updating...' : 'Confirm'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'DRAFT':
      return 'bg-amber-50 text-amber-700 dark:bg-amber-950/20 dark:text-amber-400';
    case 'READY_TO_START':
      return 'bg-blue-50 text-blue-700 dark:bg-blue-950/20 dark:text-blue-400';
    case 'ACTIVE':
      return 'bg-green-50 text-green-700 dark:bg-green-950/20 dark:text-green-400';
    case 'CANCELLED':
      return 'bg-rose-50 text-rose-700 dark:bg-rose-950/20 dark:text-rose-400';
    default:
      return 'bg-slate-50 text-slate-700 dark:bg-gray-800 dark:text-gray-400';
  }
};
