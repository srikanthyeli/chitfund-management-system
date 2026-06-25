import React, { useState } from 'react';
import { X, Gavel, Calendar, IndianRupee, Hash, FileText } from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';

interface Props {
  chitGroupId: string;
  onClose: () => void;
  onCreated: () => void;
}

const CreateAuctionDialog: React.FC<Props> = ({ chitGroupId, onClose, onCreated }) => {
  const [form, setForm] = useState({
    auction_month_number: '',
    auction_date: new Date().toISOString().split('T')[0],
    maintenance_charge: '',
    notes: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.auction_month_number || !form.maintenance_charge) {
      toast.error('Month number and maintenance charge are required');
      return;
    }
    setLoading(true);
    try {
      await api.post(`/chit-groups/${chitGroupId}/auctions`, {
        auction_month_number: parseInt(form.auction_month_number),
        auction_date: form.auction_date,
        maintenance_charge: parseFloat(form.maintenance_charge),
        notes: form.notes || null,
      });
      toast.success('Auction created successfully');
      onCreated();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to create auction');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500";
  const labelClass = "flex items-center gap-2 text-xs font-semibold mb-2 text-gray-600 dark:text-gray-400 uppercase tracking-wide";

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full sm:max-w-md bg-white dark:bg-gray-800 rounded-t-3xl sm:rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        
        {/* Colored Header Banner */}
        <div className="bg-purple-600 px-6 pt-6 pb-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-xl bg-white/20 flex items-center justify-center">
                <Gavel size={22} className="text-white" />
              </div>
              <div>
                <h2 className="font-bold text-lg text-white">New Auction</h2>
                <p className="text-xs text-purple-200">Create a monthly chit auction</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
            >
              <X size={18} className="text-white" />
            </button>
          </div>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          {/* Month Number */}
          <div>
            <label className={labelClass}>
              <Hash size={12} /> Month Number
            </label>
            <input
              type="number"
              min={1}
              value={form.auction_month_number}
              onChange={e => setForm(f => ({ ...f, auction_month_number: e.target.value }))}
              placeholder="e.g. 1"
              required
              className={inputClass}
            />
          </div>

          {/* Auction Date */}
          <div>
            <label className={labelClass}>
              <Calendar size={12} /> Auction Date
            </label>
            <input
              type="date"
              value={form.auction_date}
              onChange={e => setForm(f => ({ ...f, auction_date: e.target.value }))}
              required
              className={inputClass}
            />
          </div>

          {/* Maintenance Charge */}
          <div>
            <label className={labelClass}>
              <IndianRupee size={12} /> Maintenance Charge (₹)
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 font-semibold text-sm">₹</span>
              <input
                type="number"
                min={0}
                step="0.01"
                value={form.maintenance_charge}
                onChange={e => setForm(f => ({ ...f, maintenance_charge: e.target.value }))}
                placeholder="e.g. 4000"
                required
                className={`${inputClass} pl-8`}
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className={labelClass}>
              <FileText size={12} /> Notes <span className="font-normal normal-case text-gray-400">(optional)</span>
            </label>
            <textarea
              value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              placeholder="Any notes for this auction..."
              rows={2}
              className={`${inputClass} resize-none`}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-xl border border-gray-200 dark:border-gray-600 text-sm font-semibold text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 rounded-xl text-sm font-bold bg-purple-600 hover:bg-purple-700 text-white transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {loading ? 'Creating...' : 'Create Auction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAuctionDialog;
