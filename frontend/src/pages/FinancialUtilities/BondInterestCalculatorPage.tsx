import React, { useState } from 'react';
import { Calculator, TrendingUp, AlertTriangle, ChevronDown, ChevronUp, X } from 'lucide-react';
import { calculateBondInterest } from '../../core/bondInterestApi';
import type { BondInterestResponse } from '../../core/bondInterestApi';
import { BondStatementTemplate } from './BondStatementTemplate';
import { BondStatementActions } from './BondStatementActions';
import { useTranslation } from 'react-i18next';

const RATE_CHIPS = [2, 3, 4, 5, 6];

const fmt = (v: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(v);

const fmtDate = (d: string) =>
  new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });

const durationStr = (r: BondInterestResponse) => {
  const parts: string[] = [];
  if (r.duration_years > 0) parts.push(`${r.duration_years} Year${r.duration_years > 1 ? 's' : ''}`);
  if (r.duration_months > 0) parts.push(`${r.duration_months} Month${r.duration_months > 1 ? 's' : ''}`);
  if (r.duration_days > 0) parts.push(`${r.duration_days} Day${r.duration_days > 1 ? 's' : ''}`);
  return parts.length ? parts.join(' ') : '0 Days';
};

const todayStr = () => new Date().toISOString().split('T')[0];

export const BondInterestCalculatorPage: React.FC = () => {
  const { t } = useTranslation(['bondCalculator', 'reports']);

  const [principal, setPrincipal] = useState('');
  const [selectedRate, setSelectedRate] = useState<number | 'custom'>(3);
  const [customRate, setCustomRate] = useState('');
  const [bondStartDate, setBondStartDate] = useState('');
  const [calcDate, setCalcDate] = useState(todayStr());
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const [result, setResult] = useState<BondInterestResponse | null>(null);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const validate = () => {
    const e: Record<string, string> = {};
    if (!principal || parseFloat(principal) <= 0) e.principal = 'Principal must be greater than zero.';
    if (selectedRate === 'custom' && (!customRate || parseFloat(customRate) <= 0))
      e.rate = 'Custom rate must be greater than zero.';
    if (!bondStartDate) e.bondStartDate = 'Bond Start Date is required.';
    if (!calcDate) e.calcDate = 'Calculation Date is required.';
    else if (bondStartDate && calcDate < bondStartDate)
      e.calcDate = 'Calculation Date cannot be earlier than Bond Start Date.';
    return e;
  };

  const handleCalculate = async () => {
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length > 0) return;

    const rate = selectedRate === 'custom' ? parseFloat(customRate) : selectedRate;
    setLoading(true);
    setApiError('');
    setResult(null);
    try {
      const data = await calculateBondInterest({
        principal: parseFloat(principal),
        interest_rate: rate,
        bond_start_date: bondStartDate,
        calculation_date: calcDate,
      });
      setResult(data);
      setShowBreakdown(false);
    } catch (err: any) {
      setApiError(err?.response?.data?.message || err?.response?.data?.detail?.[0]?.msg || 'Calculation failed. Please check inputs.');
    } finally {
      setLoading(false);
    }
  };

  const isExpired = result?.bond_status === 'EXPIRED';

  const inputCls =
    'w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 transition';
  const labelCls = 'block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 uppercase tracking-wide';
  const errCls = 'text-xs text-red-500 mt-1';

  return (
    <div className="p-4 max-w-2xl mx-auto pb-32">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('bondCalculator:calculator_title')}</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Calculate Simple Interest for legally signed Bonds.
        </p>
      </div>

      {/* Input Card */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-5 space-y-5 mb-4">

        {/* Principal */}
        <div>
          <label className={labelCls}>Principal Amount</label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-semibold text-sm pointer-events-none">₹</span>
            <input
              type="number"
              min="1"
              step="any"
              placeholder="e.g. 100000"
              value={principal}
              onChange={(e) => { setPrincipal(e.target.value); setErrors((p) => ({ ...p, principal: '' })); }}
              className={`${inputCls} pl-8`}
            />
          </div>
          {errors.principal && <p className={errCls}>{errors.principal}</p>}
        </div>

        {/* Interest Rate chips */}
        <div>
          <label className={labelCls}>Interest Rate (₹ per ₹100 per month)</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {RATE_CHIPS.map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => { setSelectedRate(r); setErrors((p) => ({ ...p, rate: '' })); }}
                className={`px-4 py-2 rounded-xl text-sm font-bold border transition-all ${
                  selectedRate === r
                    ? 'bg-purple-600 text-white border-purple-600 shadow-md shadow-purple-200'
                    : 'bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-purple-400'
                }`}
              >
                ₹{r}
              </button>
            ))}
            <button
              type="button"
              onClick={() => { setSelectedRate('custom'); setErrors((p) => ({ ...p, rate: '' })); }}
              className={`px-4 py-2 rounded-xl text-sm font-bold border transition-all ${
                selectedRate === 'custom'
                  ? 'bg-purple-600 text-white border-purple-600 shadow-md shadow-purple-200'
                  : 'bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-purple-400'
              }`}
            >{t('reports:reports_custom')}</button>
          </div>
          {selectedRate === 'custom' && (
            <input
              type="number"
              min="0.01"
              step="any"
              placeholder="Enter custom rate"
              value={customRate}
              onChange={(e) => { setCustomRate(e.target.value); setErrors((p) => ({ ...p, rate: '' })); }}
              className={inputCls}
            />
          )}
          {errors.rate && <p className={errCls}>{errors.rate}</p>}
          <p className="text-[11px] text-gray-400 mt-1">
            ₹{selectedRate === 'custom' ? (customRate || '?') : selectedRate} per ₹100 ={' '}
            {selectedRate === 'custom' ? (customRate || '?') : selectedRate}% monthly interest
          </p>
        </div>

        {/* Bond Start Date */}
        <div>
          <label className={labelCls}>Bond Start Date</label>
          <input
            type="date"
            value={bondStartDate}
            onChange={(e) => { setBondStartDate(e.target.value); setErrors((p) => ({ ...p, bondStartDate: '', calcDate: '' })); }}
            className={inputCls}
          />
          {errors.bondStartDate && <p className={errCls}>{errors.bondStartDate}</p>}
        </div>

        {/* Calculation Date */}
        <div>
          <label className={labelCls}>Calculation Date</label>
          <input
            type="date"
            value={calcDate}
            min={bondStartDate || undefined}
            onChange={(e) => { setCalcDate(e.target.value); setErrors((p) => ({ ...p, calcDate: '' })); }}
            className={inputCls}
          />
          {errors.calcDate && <p className={errCls}>{errors.calcDate}</p>}
        </div>

        {/* Bond Validity read-only */}
        <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-700">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Bond Validity</span>
          <span className="text-sm font-bold text-purple-700 dark:text-purple-400">3 Years</span>
        </div>
      </div>

      {/* Calculate Button */}
      <button
        onClick={handleCalculate}
        disabled={loading}
        className="w-full py-4 bg-purple-600 hover:bg-purple-700 disabled:opacity-60 text-white text-base font-bold rounded-2xl shadow-lg shadow-purple-200 dark:shadow-none transition-all active:scale-[0.98] flex items-center justify-center gap-2"
      >
        <Calculator size={20} />
        {loading ? 'Calculating…' : 'Calculate'}
      </button>

      {apiError && (
        <p className="text-sm text-red-500 text-center mt-3">{apiError}</p>
      )}

      {/* Results */}
      {result && (
        <div className="mt-6 space-y-4">

          {/* Status Banner */}
          <div className={`flex items-center gap-3 px-4 py-3 rounded-xl font-semibold text-sm ${
            isExpired
              ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800'
              : 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800'
          }`}>
            {isExpired ? <AlertTriangle size={18} /> : <TrendingUp size={18} />}
            Bond is <strong className="ml-1">{result.bond_status}</strong>
            <span className="ml-auto text-xs font-medium opacity-70">Expires {fmtDate(result.expiry_date)}</span>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Principal</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{fmt(result.principal)}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Interest</p>
              <p className="text-xl font-bold text-purple-700 dark:text-purple-400">{fmt(result.interest)}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-4 col-span-2">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('reports:reports_total_amount')}</p>
              <p className="text-2xl font-bold" style={{ color: '#4a1c72' }}>{fmt(result.total_amount)}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-4 col-span-2">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Duration</p>
              <p className="text-lg font-bold text-gray-700 dark:text-gray-200">{durationStr(result)}</p>
            </div>
          </div>

          {/* Breakdown Toggle */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
            <button
              onClick={() => setShowBreakdown((p) => !p)}
              className="w-full flex items-center justify-between px-5 py-4 text-sm font-semibold text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              Calculation Breakdown
              {showBreakdown ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {showBreakdown && (
              <div className="px-5 pb-4 space-y-2.5 border-t border-gray-100 dark:border-gray-700 pt-3">
                {[
                  { label: 'Monthly Interest', value: fmt(result.monthly_interest) },
                  { label: 'Daily Interest (÷30)', value: fmt(result.daily_interest) },
                  { label: 'Complete Months', value: `${result.complete_months}` },
                  { label: 'Remaining Days', value: `${result.remaining_days}` },
                  { label: 'Total Interest', value: fmt(result.interest) },
                ].map(({ label, value }) => (
                  <div key={label} className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">{label}</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Expired: Renewal Info */}
          {isExpired && result.suggested_new_principal != null && (
            <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle size={16} className="text-orange-600 dark:text-orange-400" />
                <p className="text-sm font-bold text-orange-700 dark:text-orange-400">Bond Renewal Information</p>
              </div>
              {[
                { label: 'Original Principal', value: fmt(result.principal) },
                { label: 'Interest till Expiry', value: fmt(result.suggested_new_principal - result.principal) },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-sm mb-1">
                  <span className="text-orange-600 dark:text-orange-300">{label}</span>
                  <span className="font-semibold text-orange-800 dark:text-orange-200">{value}</span>
                </div>
              ))}
              <div className="flex justify-between text-sm font-bold border-t border-orange-200 dark:border-orange-700 pt-2 mt-2">
                <span className="text-orange-700 dark:text-orange-300">Suggested New Principal</span>
                <span className="text-orange-900 dark:text-orange-100">{fmt(result.suggested_new_principal)}</span>
              </div>
              <p className="text-xs text-orange-600 dark:text-orange-400 mt-2">
                Prepare a new Bond using the suggested principal amount.
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <BondStatementActions result={result} onPreview={() => setShowPreview(true)} />
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && result && (
        <div className="fixed inset-0 bg-black/60 z-50 flex flex-col overflow-y-auto">
          <div className="flex justify-end p-4 sticky top-0 z-10">
            <button
              onClick={() => setShowPreview(false)}
              className="p-2 bg-white dark:bg-gray-800 rounded-full shadow-lg text-gray-700 dark:text-gray-200 hover:bg-gray-100 transition"
            >
              <X size={22} />
            </button>
          </div>
          <div className="flex-1 flex flex-col items-center px-4 pb-8">
            <BondStatementTemplate result={result} />
            <div className="w-full max-w-[400px] mt-4">
              <BondStatementActions result={result} onPreview={() => {}} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
