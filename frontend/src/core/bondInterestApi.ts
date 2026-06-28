import api from './api';

export interface BondInterestRequest {
  principal: number;
  interest_rate: number;
  bond_start_date: string;
  calculation_date: string;
}

export interface BondInterestResponse {
  principal: number;
  interest_rate: number;
  bond_start_date: string;
  calculation_date: string;
  expiry_date: string;
  duration_years: number;
  duration_months: number;
  duration_days: number;
  monthly_interest: number;
  daily_interest: number;
  complete_months: number;
  remaining_days: number;
  interest: number;
  total_amount: number;
  bond_status: 'ACTIVE' | 'EXPIRED';
  suggested_new_principal: number | null;
}

export const calculateBondInterest = async (
  payload: BondInterestRequest
): Promise<BondInterestResponse> => {
  const { data } = await api.post('/financial-utilities/bond-interest/calculate', payload);
  return data;
};
