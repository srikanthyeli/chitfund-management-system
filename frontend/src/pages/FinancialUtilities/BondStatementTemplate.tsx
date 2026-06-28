import React from 'react';
import { BadgeIndianRupee, ShieldCheck, Calendar, TrendingUp, AlertTriangle } from 'lucide-react';
import type { BondInterestResponse } from '../../core/bondInterestApi';

interface Props {
  result: BondInterestResponse;
}

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

export const BondStatementTemplate: React.FC<Props> = ({ result }) => {
  const isExpired = result.bond_status === 'EXPIRED';

  return (
    <div className="flex justify-center shrink-0">
      <div
        id="bond-statement-capture-area"
        className="relative w-[400px] max-w-full overflow-hidden shadow-2xl sm:rounded-xl"
        style={{ minHeight: '680px', backgroundColor: '#ffffff', color: '#1f2937' }}
      >
        {/* Header */}
        <div className="pt-8 pb-12 relative text-center" style={{ backgroundColor: '#4a1c72', color: '#ffffff' }}>
          <div className="flex justify-center mb-2">
            <div className="p-3 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}>
              <BadgeIndianRupee size={36} color="#ffffff" />
            </div>
          </div>
          <h1 className="text-2xl font-bold tracking-wider leading-tight">CHITFUND</h1>
          <h2 className="text-xs font-semibold tracking-[0.2em] mb-3">MANAGEMENT</h2>
          <p className="text-xs" style={{ color: '#e9d5ff' }}>Bond Interest Statement</p>
          {/* Jagged bottom */}
          <div className="absolute bottom-0 left-0 w-full overflow-hidden leading-[0]">
            <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative block w-full h-[15px]">
              <path d="M0,0 L0,60 Q15,120 30,60 T60,60 T90,60 T120,60 T150,60 T180,60 T210,60 T240,60 T270,60 T300,60 T330,60 T360,60 T390,60 T420,60 T450,60 T480,60 T510,60 T540,60 T570,60 T600,60 T630,60 T660,60 T690,60 T720,60 T750,60 T780,60 T810,60 T840,60 T870,60 T900,60 T930,60 T960,60 T990,60 T1020,60 T1050,60 T1080,60 T1110,60 T1140,60 T1170,60 T1200,60 L1200,120 L0,120 Z" fill="#ffffff" />
            </svg>
          </div>
        </div>

        <div className="px-6 pt-6 pb-4">
          {/* Total Amount Hero */}
          <div className="text-center mb-6">
            <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: '#9333ea' }}>Total Amount Payable</p>
            <div className="text-4xl font-bold mb-1" style={{ color: '#4a1c72' }}>{fmt(result.total_amount)}</div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold mt-1"
              style={{
                backgroundColor: isExpired ? '#fee2e2' : '#dcfce7',
                color: isExpired ? '#dc2626' : '#16a34a',
              }}>
              {isExpired ? <AlertTriangle size={12} /> : <ShieldCheck size={12} />}
              {result.bond_status}
            </div>
          </div>

          {/* Date + Duration row */}
          <div className="rounded-xl p-4 flex justify-between items-center mb-5" style={{ backgroundColor: '#faf5ff' }}>
            <div className="flex items-center gap-2">
              <Calendar size={18} color="#9333ea" />
              <div>
                <div className="text-[10px] font-semibold uppercase" style={{ color: '#6b7280' }}>Bond Date</div>
                <div className="text-xs font-bold" style={{ color: '#374151' }}>{fmtDate(result.bond_start_date)}</div>
              </div>
            </div>
            <div className="w-px h-8" style={{ backgroundColor: '#e9d5ff' }} />
            <div className="text-right">
              <div className="text-[10px] font-semibold uppercase" style={{ color: '#6b7280' }}>Calc Date</div>
              <div className="text-xs font-bold" style={{ color: '#374151' }}>{fmtDate(result.calculation_date)}</div>
            </div>
          </div>

          {/* Key Details */}
          {[
            { label: 'Principal', value: fmt(result.principal) },
            { label: 'Interest Rate', value: `₹${result.interest_rate} per ₹100/month` },
            { label: 'Duration', value: durationStr(result) },
            { label: 'Interest', value: fmt(result.interest), highlight: true },
            { label: 'Total Amount', value: fmt(result.total_amount), bold: true },
            { label: 'Bond Expiry', value: fmtDate(result.expiry_date) },
          ].map(({ label, value, highlight, bold }) => (
            <div key={label} className="flex justify-between items-center py-2.5 border-b" style={{ borderColor: '#f3f4f6' }}>
              <span className="text-xs font-medium" style={{ color: '#6b7280' }}>{label}</span>
              <span className={`text-xs font-bold ${highlight ? 'text-purple-700' : bold ? 'text-gray-900' : ''}`}
                style={bold ? { color: '#4a1c72' } : highlight ? { color: '#7e22ce' } : { color: '#111827' }}>
                {value}
              </span>
            </div>
          ))}

          {/* Breakdown */}
          <div className="mt-4 rounded-xl p-4" style={{ backgroundColor: '#faf5ff' }}>
            <p className="text-[10px] font-bold uppercase tracking-widest mb-3" style={{ color: '#7e22ce' }}>Calculation Breakdown</p>
            {[
              { label: 'Monthly Interest', value: fmt(result.monthly_interest) },
              { label: 'Daily Interest', value: fmt(result.daily_interest) },
              { label: 'Complete Months', value: `${result.complete_months}` },
              { label: 'Remaining Days', value: `${result.remaining_days}` },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between text-[11px] py-1">
                <span style={{ color: '#6b7280' }}>{label}</span>
                <span className="font-semibold" style={{ color: '#374151' }}>{value}</span>
              </div>
            ))}
          </div>

          {/* Expired: Suggested New Principal */}
          {isExpired && result.suggested_new_principal != null && (
            <div className="mt-4 rounded-xl p-4 border" style={{ backgroundColor: '#fff7ed', borderColor: '#fed7aa' }}>
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp size={16} color="#ea580c" />
                <p className="text-xs font-bold" style={{ color: '#c2410c' }}>Bond Expired — Renewal Info</p>
              </div>
              <div className="flex justify-between text-xs">
                <span style={{ color: '#9a3412' }}>Suggested New Principal</span>
                <span className="font-bold" style={{ color: '#9a3412' }}>{fmt(result.suggested_new_principal)}</span>
              </div>
              <p className="text-[10px] mt-2" style={{ color: '#c2410c' }}>
                Prepare a new Bond using the suggested principal amount.
              </p>
            </div>
          )}

          {/* Generated date */}
          <p className="text-center text-[10px] mt-5 mb-4" style={{ color: '#9ca3af' }}>
            Generated on {new Date().toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
          </p>
        </div>

        {/* Footer bar */}
        <div className="py-3 px-4 flex justify-between items-center" style={{ backgroundColor: '#faf5ff' }}>
          {['Secure', 'Transparent', 'Reliable'].map((t, i) => (
            <React.Fragment key={t}>
              <div className="flex items-center gap-1 text-[10px] font-medium" style={{ color: '#7e22ce' }}>
                <ShieldCheck size={12} color="#7e22ce" />{t}
              </div>
              {i < 2 && <div className="w-1 h-1 rounded-full" style={{ backgroundColor: '#d8b4fe' }} />}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
