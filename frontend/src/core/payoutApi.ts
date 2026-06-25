import api from './api';

export interface PayoutPreviewResponse {
  month_number: number;
  winner: {
    member_name: string;
    share_count: number;
  };
  auction: {
    gross_chit_amount: number;
    winning_bid_discount_amount: number;
    maintenance_charge_amount: number;
    payout_amount: number;
  };
  collection: {
    expected_collection_amount: number;
    actual_collection_amount: number;
    pending_collection_amount: number;
  };
  payout_eligibility: {
    can_pay_from_collection: boolean;
    minimum_organizer_contribution_required: number;
    payout_exists: boolean;
  };
}

export const payoutApi = {
  getPayoutPreview: async (chitGroupId: string, monthNumber: number): Promise<PayoutPreviewResponse> => {
    const response = await api.get(`/chit-groups/${chitGroupId}/months/${monthNumber}/winner-payout-preview`);
    return response.data;
  },

  createPayout: async (chitGroupId: string, monthNumber: number, payload: any) => {
    // Kept for backward compatibility if used elsewhere, although we should use createDraft
    const response = await api.post(`/chit-groups/${chitGroupId}/months/${monthNumber}/winner-payouts`, payload);
    return response.data;
  },

  closeMonth: async (chitGroupId: string, monthNumber: number, payload: any) => {
    const response = await api.post(`/chit-groups/${chitGroupId}/months/${monthNumber}/financial-close`, payload);
    return response.data;
  },

  getFinancialSummary: async (chitGroupId: string) => {
    const response = await api.get(`/chit-groups/${chitGroupId}/financial-summary`);
    return response.data;
  },

  // --- Phase 6.1 Endpoints ---
  
  createDraft: async (payload: any) => {
    const response = await api.post(`/winner-payouts`, payload);
    return response.data;
  },

  listPayouts: async (limit = 50, offset = 0) => {
    const response = await api.get(`/winner-payouts?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  getPayout: async (payoutId: string) => {
    const response = await api.get(`/winner-payouts/${payoutId}`);
    return response.data;
  },

  markPaid: async (payoutId: string, payload: any) => {
    const response = await api.post(`/winner-payouts/${payoutId}/mark-paid`, payload);
    return response.data;
  },

  shareReceipt: async (payoutId: string) => {
    const response = await api.post(`/winner-payouts/${payoutId}/share`);
    return response.data;
  },

  confirmReceived: async (payoutId: string, payload: any) => {
    const response = await api.post(`/winner-payouts/${payoutId}/confirm-received`, payload);
    return response.data;
  }
};
