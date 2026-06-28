import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  CheckCircle2, XCircle, Calendar, Users, User, Phone,
  IndianRupee, CreditCard, ShieldCheck, BadgeIndianRupee, Hash
} from 'lucide-react';

export interface WinnerPayoutReceiptData {
  payout_receipt_number: string;
  payout_amount: number;
  payout_date: string;
  status: string;
  winner_name: string;
  winner_phone: string;
  chit_name: string;
  month_number: number;
  gross_chit_amount: number;
  winning_bid_discount_amount: number;
  maintenance_charge_amount: number;
  payment_method: string;
  transaction_reference?: string;
}

interface Props {
  receiptData: WinnerPayoutReceiptData;
}

export const WinnerPayoutReceiptTemplate: React.FC<Props> = ({ receiptData }) => {
  const { t } = useTranslation('common');
  const isReversed = receiptData.status === 'REVERSED';
  const fmt = (v: number) =>
    new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v);

  return (
    <div style={{ display: 'flex', justifyContent: 'center', flexShrink: 0 }}>
      <div
        id="winner-receipt-capture-area"
        style={{
          position: 'relative', width: '400px', maxWidth: '100%', overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)', borderRadius: '12px',
          minHeight: '680px', backgroundColor: '#ffffff', color: '#1f2937',
        }}
      >
        {isReversed && (
          <div style={{
            position: 'absolute', inset: 0, zIndex: 50, display: 'flex',
            alignItems: 'center', justifyContent: 'center', pointerEvents: 'none', opacity: 0.2,
          }}>
            <span style={{ fontSize: '60px', fontWeight: 'bold', transform: 'rotate(-45deg)', color: '#dc2626' }}>
              REVERSED
            </span>
          </div>
        )}

        {/* Header */}
        <div style={{ paddingTop: '32px', paddingBottom: '48px', position: 'relative', textAlign: 'center', backgroundColor: '#065f46', color: '#ffffff' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '8px' }}>
            <div style={{ padding: '12px', borderRadius: '50%', backgroundColor: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <BadgeIndianRupee size={36} color="#ffffff" />
            </div>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', letterSpacing: '0.1em', margin: 0 }}>CHITFUND</h1>
          <h2 style={{ fontSize: '11px', fontWeight: '600', letterSpacing: '0.2em', margin: '2px 0 12px' }}>{t('receipt_winner')}</h2>
          <p style={{ fontSize: '11px', color: '#a7f3d0', margin: 0 }}>{t('receipt_congratulations', { name: receiptData.winner_name.split(' ')[0] })}</p>
          <div style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', overflow: 'hidden', lineHeight: 0 }}>
            <svg viewBox="0 0 1200 120" preserveAspectRatio="none" style={{ display: 'block', width: '100%', height: '15px' }}>
              <path d="M0,0 L0,60 Q15,120 30,60 T60,60 T90,60 T120,60 T150,60 T180,60 T210,60 T240,60 T270,60 T300,60 T330,60 T360,60 T390,60 T420,60 T450,60 T480,60 T510,60 T540,60 T570,60 T600,60 T630,60 T660,60 T690,60 T720,60 T750,60 T780,60 T810,60 T840,60 T870,60 T900,60 T930,60 T960,60 T990,60 T1020,60 T1050,60 T1080,60 T1110,60 T1140,60 T1170,60 T1200,60 L1200,120 L0,120 Z" fill="#ffffff" />
            </svg>
          </div>
        </div>

        {/* Amount Section */}
        <div style={{ padding: '24px 24px 16px', textAlign: 'center' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '12px' }}>
            {isReversed
              ? <XCircle size={40} color="#ef4444" fill="#fef2f2" />
              : <CheckCircle2 size={40} color="#22c55e" fill="#f0fdf4" />
            }
          </div>
          <h3 style={{ fontSize: '13px', fontWeight: 'bold', letterSpacing: '0.1em', marginBottom: '8px', color: isReversed ? '#dc2626' : '#16a34a' }}>
            {isReversed ? t('receipt_payout_reversed') : t('receipt_payout_disbursed')}
          </h3>
          <div style={{ fontSize: '40px', fontWeight: 'bold', marginBottom: '4px', color: '#065f46' }}>
            ₹{fmt(receiptData.payout_amount)}
          </div>
          <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '24px' }}>{t('receipt_net_amount_paid')}</p>

          {/* Date & Receipt No */}
          <div style={{ borderRadius: '12px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', backgroundColor: '#f0fdf4' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Calendar size={18} color="#16a34a" />
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: '10px', fontWeight: '600', textTransform: 'uppercase', color: '#6b7280' }}>
                  {new Date(receiptData.payout_date).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                </div>
              </div>
            </div>
            <div style={{ width: '1px', height: '32px', backgroundColor: '#bbf7d0' }} />
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '10px', fontWeight: '600', textTransform: 'uppercase', color: '#6b7280' }}>{t('receipt_receipt_no')}</div>
              <div style={{ fontSize: '10px', fontFamily: 'monospace', fontWeight: 'bold', color: '#14532d' }}>{receiptData.payout_receipt_number}</div>
            </div>
          </div>

          {/* Winner & Chit Info */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
            <div style={{ flex: 1, border: '1px solid #f3f4f6', borderRadius: '12px', padding: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f9fafb' }}>
              <div style={{ padding: '8px', borderRadius: '50%', marginBottom: '8px', backgroundColor: '#dcfce7' }}>
                <Users size={16} color="#15803d" />
              </div>
              <div style={{ fontSize: '9px', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '4px', color: '#16a34a' }}>{t('receipt_chit_fund')}</div>
              <div style={{ fontSize: '12px', fontWeight: '600', textAlign: 'center', marginBottom: '4px', color: '#1f2937' }}>{receiptData.chit_name}</div>
              <div style={{ fontSize: '10px', color: '#6b7280' }}>{t('receipt_month')} <strong style={{ color: '#374151' }}>{receiptData.month_number}</strong></div>
            </div>
            <div style={{ flex: 1, border: '1px solid #f3f4f6', borderRadius: '12px', padding: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f9fafb' }}>
              <div style={{ padding: '8px', borderRadius: '50%', marginBottom: '8px', backgroundColor: '#dcfce7' }}>
                <User size={16} color="#15803d" />
              </div>
              <div style={{ fontSize: '9px', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '4px', color: '#16a34a' }}>{t('receipt_winner')}</div>
              <div style={{ fontSize: '12px', fontWeight: '600', textAlign: 'center', marginBottom: '4px', color: '#1f2937' }}>{receiptData.winner_name}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: '#4b5563' }}>
                <Phone size={10} />{receiptData.winner_phone}
              </div>
            </div>
          </div>

          {/* Calculation Breakdown */}
          <div style={{ marginBottom: '24px' }}>
            {[
              { label: t('receipt_gross_chit_amount'), value: `₹${fmt(receiptData.gross_chit_amount)}`, color: '#111827' },
              { label: t('receipt_winning_bid_discount'), value: `- ₹${fmt(receiptData.winning_bid_discount_amount)}`, color: '#ef4444' },
              { label: t('receipt_maintenance_charge'), value: `- ₹${fmt(receiptData.maintenance_charge_amount)}`, color: '#ef4444' },
            ].map((row, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid #f3f4f6', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <IndianRupee size={16} color="#bbf7d0" />
                  <span style={{ fontSize: '12px', fontWeight: '500', color: '#374151' }}>{row.label}</span>
                </div>
                <span style={{ fontSize: '12px', fontWeight: 'bold', color: row.color }}>{row.value}</span>
              </div>
            ))}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '8px' }}>
              <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#374151' }}>{t('receipt_net_payout')}</span>
              <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#065f46' }}>₹{fmt(receiptData.payout_amount)}</span>
            </div>
          </div>

          {/* Payment Meta */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
            <div style={{ flex: 1, borderRadius: '8px', padding: '8px', display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: '#f9fafb' }}>
              <div style={{ padding: '6px', borderRadius: '4px', backgroundColor: '#ffffff', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <CreditCard size={14} color="#16a34a" />
              </div>
              <div>
                <div style={{ fontSize: '9px', color: '#6b7280' }}>{t('receipt_payment_mode')}</div>
                <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#1f2937' }}>{receiptData.payment_method}</div>
              </div>
            </div>
            {receiptData.transaction_reference && (
              <div style={{ flex: 1, borderRadius: '8px', padding: '8px', display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: '#f9fafb' }}>
                <div style={{ padding: '6px', borderRadius: '4px', backgroundColor: '#ffffff', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                  <Hash size={14} color="#16a34a" />
                </div>
                <div>
                  <div style={{ fontSize: '9px', color: '#6b7280' }}>{t('receipt_transaction_ref')}</div>
                  <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#1f2937', maxWidth: '80px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {receiptData.transaction_reference}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div style={{ borderTop: '1px dashed #d1d5db', margin: '16px 0' }} />

          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <h4 style={{ fontFamily: 'serif', fontStyle: 'italic', fontSize: '18px', marginBottom: '4px', color: '#065f46' }}>
              {t('receipt_congratulations', { name: receiptData.winner_name.split(' ')[0] })}
            </h4>
            <p style={{ fontSize: '10px', color: '#6b7280', margin: 0 }}>{t('receipt_system_generated')}</p>
          </div>
        </div>

        {/* Footer Bar */}
        <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f0fdf4' }}>
          {[t('receipt_secure'), t('receipt_transparent'), t('receipt_reliable')].map((label, i) => (
            <React.Fragment key={label}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', fontWeight: '500', color: '#15803d' }}>
                <ShieldCheck size={12} color="#15803d" />{label}
              </div>
              {i < 2 && <div style={{ width: '4px', height: '4px', borderRadius: '50%', backgroundColor: '#bbf7d0' }} />}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
