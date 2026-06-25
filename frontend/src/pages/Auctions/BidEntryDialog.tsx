import React, { useState } from 'react';
import { X, IndianRupee, MessageSquare, ChevronDown } from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';

interface EligibleMember {
  membership_id: string;
  member_id: string;
  member_code: string;
  full_name: string;
  share_count: number;
  has_won_auction: boolean;
}

interface Props {
  auctionId: string;
  maxBid: number;
  auctionMonth: number;
  eligibleMembers: EligibleMember[];
  onClose: () => void;
  onBidPlaced: () => void;
}

const fmt = (v: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(v);

const BidEntryDialog: React.FC<Props> = ({ auctionId, maxBid, auctionMonth, eligibleMembers, onClose, onBidPlaced }) => {
  const [membershipId, setMembershipId] = useState('');
  const [bidAmount, setBidAmount] = useState('');
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);

  const eligible = eligibleMembers.filter(m => !m.has_won_auction);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!membershipId) { toast.error('Please select a member'); return; }
    const amount = parseFloat(bidAmount);
    if (!amount || amount <= 0) { toast.error('Enter a valid bid amount'); return; }
    if (amount > maxBid) { toast.error(`Bid cannot exceed maximum allowed ₹${maxBid}`); return; }

    setLoading(true);
    try {
      await api.post(`/chit-auctions/${auctionId}/bids`, {
        membership_id: membershipId,
        bid_discount_amount: amount,
        remarks: remarks || null,
      });
      toast.success('Bid submitted successfully');
      onBidPlaced();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to submit bid');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm">
      <div
        className="w-full sm:max-w-md rounded-t-3xl sm:rounded-2xl border p-6 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 shadow-xl"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-bold text-lg text-gray-900 dark:text-white">Submit Bid</h2>
            <p className="text-xs text-gray-500">Month {auctionMonth} · Max {fmt(maxBid)}</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-500">
            <X size={18} />
          </button>
        </div>

        {eligible.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>No eligible members available to bid.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Member Select */}
            <div>
              <label className="text-xs font-semibold mb-2 block text-gray-500">Select Member</label>
              <div className="relative">
                <select
                  value={membershipId}
                  onChange={e => setMembershipId(e.target.value)}
                  required
                  className="w-full px-4 py-3 pr-10 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm outline-none appearance-none focus:ring-2 focus:ring-purple-600 text-gray-900 dark:text-white"
                >
                  <option value="">-- Choose Member --</option>
                  {eligible.map(m => (
                    <option key={m.membership_id} value={m.membership_id}>
                      {m.full_name} ({m.member_code}) · {m.share_count} share{m.share_count > 1 ? 's' : ''}
                    </option>
                  ))}
                </select>
                <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500" />
              </div>
            </div>

            {/* Bid Amount */}
            <div>
              <label className="flex items-center gap-2 text-xs font-semibold mb-2 text-gray-500">
                <IndianRupee size={12} /> Bid Discount Amount (₹)
              </label>
              <input
                type="number"
                min={1}
                max={maxBid}
                step="0.01"
                value={bidAmount}
                onChange={e => setBidAmount(e.target.value)}
                placeholder={`Max ${maxBid}`}
                required
                className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-600 text-gray-900 dark:text-white"
              />
              <p className="text-xs mt-1 text-gray-500">
                Maximum allowed: <span className="font-semibold">{fmt(maxBid)}</span>
              </p>
            </div>

            {/* Remarks */}
            <div>
              <label className="flex items-center gap-2 text-xs font-semibold mb-2 text-gray-500">
                <MessageSquare size={12} /> Remarks (optional)
              </label>
              <input
                type="text"
                value={remarks}
                onChange={e => setRemarks(e.target.value)}
                placeholder="e.g. Urgent medical need"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-600 text-gray-900 dark:text-white"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button type="button" onClick={onClose} className="flex-1 py-3 rounded-xl border border-gray-300 dark:border-gray-700 text-sm font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-300">
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-3 rounded-xl text-sm font-semibold transition-all active:scale-95 disabled:opacity-50 bg-purple-600 hover:bg-purple-700 text-white"
              >
                {loading ? 'Submitting...' : 'Submit Bid'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default BidEntryDialog;
