import api from './api';

export interface CollectionSummaryResponse {
  chit_group_id: string;
  auction_id: string;
  month_number: number;
  summary: {
    total_memberships: number;
    total_net_payable: number;
    total_collected: number;
    total_remaining: number;
    paid_count: number;
    partial_count: number;
    pending_count: number;
    overdue_count: number;
  };
  dues: any[];
}

export const chitCollectionApi = {
  getActiveCollections: async () => {
    const response = await api.get('/collections/active');
    return response.data;
  },

  getCollectionSummary: async (chitGroupId: string, auctionId: string): Promise<CollectionSummaryResponse> => {
    const response = await api.get(`/chit-groups/${chitGroupId}/auctions/${auctionId}/collections`);
    return response.data;
  },

  collectPayment: async (dueId: string, payload: any) => {
    const response = await api.post(`/monthly-member-dues/${dueId}/payments`, payload);
    return response.data;
  },

  getPaymentHistory: async (dueId: string) => {
    const response = await api.get(`/monthly-member-dues/${dueId}/payments`);
    return response.data;
  },

  reversePayment: async (receiptId: string, payload: any) => {
    const response = await api.post(`/chit-payment-receipts/${receiptId}/reverse`, payload);
    return response.data;
  },

  getMemberPassbook: async (memberId: string) => {
    const response = await api.get(`/members/${memberId}/passbook`);
    return response.data;
  }
};
