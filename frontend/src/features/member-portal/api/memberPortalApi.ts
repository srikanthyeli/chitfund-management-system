import api from '../../../core/api';

export interface MemberDashboardStats {
  active_chit_groups: number;
  total_shares_held: number;
  current_month_due: number;
  pending_overdue_amount: number;
  payments_made_this_month: number;
  total_dividends_earned: number;
}

export interface UpcomingDueResponse {
  chit_group_id: string;
  chit_group_name: string;
  month_number: number;
  due_date: string | null;
  amount_due: number;
  status: string;
}

export interface RecentPaymentResponse {
  receipt_id: string;
  receipt_number: string;
  chit_group_name: string;
  amount: number;
  payment_date: string;
  status: string;
}

export interface RecentAuctionResponse {
  auction_id: string;
  chit_group_name: string;
  month_number: number;
  winner_name: string | null;
  winning_discount: number;
  dividend_per_share: number;
  auction_date: string;
}

export interface WinnerPayoutPreviewResponse {
  payout_id: string;
  status: string;
  net_payout_amount: number;
}

export interface MemberDashboardResponse {
  stats: MemberDashboardStats;
  upcoming_dues: UpcomingDueResponse[];
  recent_payments: RecentPaymentResponse[];
  recent_auctions: RecentAuctionResponse[];
  winner_payouts: WinnerPayoutPreviewResponse[];
}

export interface ChitSummaryResponse {
  chit_group_id: string;
  chit_group_name: string;
  chit_code: string;
  organizer_name: string;
  start_date: string;
  duration_months: number;
  current_month: number;
  status: string;
  shares_held: number;
  monthly_installment_per_share: number;
  total_monthly_payable: number;
  next_due_date: string | null;
  current_payment_status: string;
}

export const memberPortalApi = {
  getDashboard: async (): Promise<MemberDashboardResponse> => {
    const response = await api.get('/member-portal/dashboard');
    return response.data;
  },

  listChits: async (): Promise<ChitSummaryResponse[]> => {
    const response = await api.get('/member-portal/chits');
    return response.data;
  },
  
  getNotifications: async (page = 1, pageSize = 20) => {
    const response = await api.get('/member-portal/notifications', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }
};
