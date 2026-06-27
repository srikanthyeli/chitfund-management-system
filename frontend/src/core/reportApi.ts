import api from './api';

export interface ReportParams {
  page?: number;
  limit?: number;
  date_from?: string;
  date_to?: string;
  month?: number;
  year?: number;
  member_id?: string;
  chit_group_id?: string;
  export?: boolean;
}

export const reportApi = {
  getDashboardMetrics: async () => {
    const response = await api.get('/reports/dashboard');
    return response.data;
  },

  getCollectionsReport: async (params: ReportParams = {}) => {
    const response = await api.get('/reports/collections', { params });
    return response.data;
  },

  getPendingCollectionsReport: async (params: ReportParams = {}) => {
    const response = await api.get('/reports/pending-collections', { params });
    return response.data;
  },

  getAuctionReport: async (params: ReportParams = {}) => {
    const response = await api.get('/reports/auctions', { params });
    return response.data;
  },

  getWinnerPayoutReport: async (params: ReportParams = {}) => {
    const response = await api.get('/reports/winner-payouts', { params });
    return response.data;
  },

  getMemberFinancialReport: async (params: ReportParams = {}) => {
    const response = await api.get('/reports/member-financial', { params });
    return response.data;
  },

  getOrganizerFinancialReport: async (params: ReportParams = {}) => {
    const response = await api.get('/reports/organizer-financial', { params });
    return response.data;
  },

  getChitPerformanceReport: async (params: ReportParams = {}) => {
    const response = await api.get('/reports/chit-performance', { params });
    return response.data;
  },
};
