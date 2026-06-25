import React, { useState } from 'react';
import { X } from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';

interface ChangeMobileDialogProps {
  isOpen: boolean;
  onClose: () => void;
  memberId: string;
  currentMobile: string;
  onSuccess: (updatedMember: any) => void;
}

export const ChangeMobileDialog: React.FC<ChangeMobileDialogProps> = ({
  isOpen,
  onClose,
  memberId,
  currentMobile,
  onSuccess,
}) => {
  const [oldMobile, setOldMobile] = useState('');
  const [newMobile, setNewMobile] = useState('');
  const [confirmNewMobile, setConfirmNewMobile] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!oldMobile || !newMobile || !confirmNewMobile) {
      toast.error('All fields are required');
      return;
    }

    if (newMobile !== confirmNewMobile) {
      toast.error('New mobile and confirmation do not match');
      return;
    }

    setLoading(false);
    try {
      setLoading(true);
      const response = await api.patch(`/members/${memberId}/mobile`, {
        old_mobile: oldMobile,
        new_mobile: newMobile,
        confirm_new_mobile: confirmNewMobile,
      });
      toast.success('Mobile number updated successfully');
      onSuccess(response.data);
      onClose();
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to update mobile number');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-md overflow-hidden shadow-xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700 bg-slate-50 dark:bg-gray-850">
          <h3 className="font-bold text-gray-900 dark:text-white">Change Mobile Number</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full">
            <X size={20} className="text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">
              Current Mobile (Stored on Profile)
            </label>
            <input
              type="text"
              disabled
              value={currentMobile}
              className="w-full px-4 py-2 rounded-xl bg-gray-100 dark:bg-gray-700 text-gray-500 cursor-not-allowed border-none text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">
              Enter Current Mobile (Confirm Identity)
            </label>
            <input
              type="text"
              required
              placeholder="e.g. 9876543210"
              value={oldMobile}
              onChange={(e) => setOldMobile(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">
              Enter New Mobile
            </label>
            <input
              type="text"
              required
              placeholder="e.g. 9988776655"
              value={newMobile}
              onChange={(e) => setNewMobile(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">
              Confirm New Mobile
            </label>
            <input
              type="text"
              required
              placeholder="Re-enter new mobile"
              value={confirmNewMobile}
              onChange={(e) => setConfirmNewMobile(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>

          <div className="flex space-x-3 pt-3 border-t border-gray-100 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 rounded-xl bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors disabled:opacity-50"
            >
              {loading ? 'Updating...' : 'Update Mobile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
