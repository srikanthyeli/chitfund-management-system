import React from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Calendar, 
  Users, 
  User, 
  Phone, 
  FileText, 
  Wallet, 
  IndianRupee, 
  ClipboardCheck, 
  CreditCard, 
  ShieldCheck,
  BadgeIndianRupee
} from 'lucide-react';

interface ReceiptProps {
  receiptData: {
    receipt_number: string;
    payment_amount: number;
    payment_date: string;
    status: string; // SUCCESS, REVERSED
    member_name: string;
    member_phone: string;
    chit_name: string;
    month_number: number;
    share_count: number;
    gross_installment_amount: number;
    bonus_per_share: number;
    total_bonus_amount: number;
    net_payable: number;
    remaining_balance: number;
    payment_method: string;
    collected_by: string;
    payment_status: string; // PAID, PARTIALLY_PAID
  };
}

export const PaymentReceiptTemplate: React.FC<ReceiptProps> = ({ receiptData }) => {
  const isReversed = receiptData.status === 'REVERSED';
  const isFullyPaid = receiptData.payment_status === 'PAID';

  return (
    <div className="flex justify-center shrink-0">
      <div 
        id="receipt-capture-area" 
        className="relative w-[400px] max-w-full overflow-hidden shadow-2xl sm:rounded-xl"
        style={{ minHeight: '700px', backgroundColor: '#ffffff', color: '#1f2937' }}
      >
        {isReversed && (
          <div className="absolute inset-0 z-50 flex items-center justify-center pointer-events-none opacity-20">
            <span className="text-6xl font-bold -rotate-45" style={{ color: '#dc2626' }}>REVERSED</span>
          </div>
        )}

        {/* Header Section */}
        <div className="pt-8 pb-12 relative text-center" style={{ backgroundColor: '#4a1c72', color: '#ffffff' }}>
          <div className="flex justify-center mb-2">
            <div className="p-3 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
              <BadgeIndianRupee size={36} color="#ffffff" />
            </div>
          </div>
          <h1 className="text-2xl font-bold tracking-wider leading-tight">CHITFUND</h1>
          <h2 className="text-xs font-semibold tracking-[0.2em] mb-3">MANAGEMENT</h2>
          <p className="text-xs" style={{ color: '#e9d5ff' }}>Trusted by Families. Managed with Care.</p>
          
          {/* Jagged Bottom Edge */}
          <div className="absolute bottom-0 left-0 w-full overflow-hidden leading-[0]">
            <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative block w-full h-[15px]">
              <path d="M0,0 L0,60 Q15,120 30,60 T60,60 T90,60 T120,60 T150,60 T180,60 T210,60 T240,60 T270,60 T300,60 T330,60 T360,60 T390,60 T420,60 T450,60 T480,60 T510,60 T540,60 T570,60 T600,60 T630,60 T660,60 T690,60 T720,60 T750,60 T780,60 T810,60 T840,60 T870,60 T900,60 T930,60 T960,60 T990,60 T1020,60 T1050,60 T1080,60 T1110,60 T1140,60 T1170,60 T1200,60 L1200,120 L0,120 Z" fill="#ffffff"></path>
            </svg>
          </div>
        </div>

        {/* Amount Section */}
        <div className="px-6 pt-6 pb-4 text-center">
          <div className="flex justify-center mb-3">
            {isReversed ? (
              <XCircle size={40} color="#ef4444" fill="#fef2f2" />
            ) : (
              <CheckCircle2 size={40} color="#22c55e" fill="#f0fdf4" />
            )}
          </div>
          <h3 className="text-sm font-bold tracking-wider mb-2" style={{ color: isReversed ? '#dc2626' : '#16a34a' }}>
            {isReversed ? 'PAYMENT REVERSED' : 'PAYMENT RECEIVED'}
          </h3>
          <div className="text-4xl font-bold mb-1 flex justify-center items-center" style={{ color: '#4a1c72' }}>
            ₹{receiptData.payment_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-xs mb-6" style={{ color: '#6b7280' }}>
            Amount Paid Successfully
          </p>

          {/* Date & Receipt No Block */}
          <div className="rounded-xl p-4 flex justify-between items-center mb-6" style={{ backgroundColor: '#faf5ff' }}>
            <div className="flex items-center gap-2">
              <Calendar size={18} color="#9333ea" />
              <div className="text-left">
                <div className="text-[10px] font-semibold uppercase" style={{ color: '#6b7280' }}>
                  {new Date(receiptData.payment_date).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                </div>
                <div className="text-[10px] font-medium" style={{ color: '#374151' }}>
                  {new Date(receiptData.payment_date).toLocaleString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })}
                </div>
              </div>
            </div>
            <div className="w-px h-8" style={{ backgroundColor: '#e9d5ff' }}></div>
            <div className="text-right">
              <div className="text-[10px] font-semibold uppercase" style={{ color: '#6b7280' }}>Receipt No.</div>
              <div className="text-[10px] font-mono font-bold" style={{ color: '#581c87' }}>{receiptData.receipt_number}</div>
            </div>
          </div>

          {/* Chit & Member Info */}
          <div className="flex gap-2 mb-6">
            <div className="flex-1 border rounded-xl p-3 flex flex-col items-center shadow-sm" style={{ borderColor: '#f3f4f6', backgroundColor: '#f9fafb' }}>
              <div className="p-2 rounded-full mb-2" style={{ backgroundColor: '#f3e8ff' }}>
                <Users size={16} color="#7e22ce" />
              </div>
              <div className="text-[9px] font-bold uppercase tracking-wider mb-1" style={{ color: '#9333ea' }}>Chit Fund</div>
              <div className="text-xs font-semibold text-center mb-1" style={{ color: '#1f2937' }}>{receiptData.chit_name}</div>
              <div className="flex justify-between w-full text-[10px] mt-auto" style={{ color: '#6b7280' }}>
                <span>Month <strong style={{ color: '#374151' }}>{receiptData.month_number}</strong></span>
                <span>Shares <strong style={{ color: '#374151' }}>{receiptData.share_count}</strong></span>
              </div>
            </div>
            <div className="flex-1 border rounded-xl p-3 flex flex-col items-center shadow-sm" style={{ borderColor: '#f3f4f6', backgroundColor: '#f9fafb' }}>
              <div className="p-2 rounded-full mb-2" style={{ backgroundColor: '#f3e8ff' }}>
                <User size={16} color="#7e22ce" />
              </div>
              <div className="text-[9px] font-bold uppercase tracking-wider mb-1" style={{ color: '#9333ea' }}>Member</div>
              <div className="text-xs font-semibold text-center mb-1" style={{ color: '#1f2937' }}>{receiptData.member_name}</div>
              <div className="flex items-center gap-1 text-[10px] mt-auto" style={{ color: '#4b5563' }}>
                <Phone size={10} />
                <span>{receiptData.member_phone}</span>
              </div>
            </div>
          </div>

          {/* Payment Details */}
          <div className="mb-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b" style={{ borderColor: '#f3f4f6' }}>
              <div className="flex items-center gap-2">
                <FileText size={16} color="#d8b4fe" />
                <span className="text-xs font-medium" style={{ color: '#374151' }}>Monthly Due (Net Payable)</span>
              </div>
              <span className="text-xs font-bold" style={{ color: '#111827' }}>₹{receiptData.net_payable.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
            
            <div className="flex justify-between items-center pb-3 border-b" style={{ borderColor: '#f3f4f6' }}>
              <div className="flex items-center gap-2">
                <Wallet size={16} color="#d8b4fe" />
                <span className="text-xs font-medium" style={{ color: '#374151' }}>Paid This Time</span>
              </div>
              <span className="text-xs font-bold" style={{ color: '#16a34a' }}>₹{receiptData.payment_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
            
            <div className="flex justify-between items-center pb-3 border-b" style={{ borderColor: '#f3f4f6' }}>
              <div className="flex items-center gap-2">
                <IndianRupee size={16} color="#d8b4fe" />
                <span className="text-xs font-medium" style={{ color: '#374151' }}>Remaining Balance</span>
              </div>
              <span className="text-xs font-bold" style={{ color: '#4a1c72' }}>₹{receiptData.remaining_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <ClipboardCheck size={16} color="#d8b4fe" />
                <span className="text-xs font-medium" style={{ color: '#374151' }}>Payment Status</span>
              </div>
              <span className="text-[10px] font-bold px-3 py-1 rounded-full" style={{ 
                backgroundColor: isFullyPaid ? '#dcfce7' : '#ffedd5',
                color: isFullyPaid ? '#15803d' : '#c2410c'
              }}>
                {isFullyPaid ? 'FULLY PAID' : 'PARTIALLY PAID'}
              </span>
            </div>
          </div>

          {/* Meta Info */}
          <div className="flex gap-2 mb-6">
             <div className="flex-1 rounded-lg p-2 flex items-center gap-2" style={{ backgroundColor: '#f9fafb' }}>
                <div className="p-1.5 rounded shadow-sm" style={{ backgroundColor: '#ffffff' }}>
                  <CreditCard size={14} color="#a855f7" />
                </div>
                <div>
                  <div className="text-[9px]" style={{ color: '#6b7280' }}>Payment Method</div>
                  <div className="text-[10px] font-bold" style={{ color: '#1f2937' }}>{receiptData.payment_method}</div>
                </div>
             </div>
             <div className="flex-1 rounded-lg p-2 flex items-center gap-2" style={{ backgroundColor: '#f9fafb' }}>
                <div className="p-1.5 rounded shadow-sm" style={{ backgroundColor: '#ffffff' }}>
                  <User size={14} color="#a855f7" />
                </div>
                <div>
                  <div className="text-[9px]" style={{ color: '#6b7280' }}>Collected By</div>
                  <div className="text-[10px] font-bold truncate max-w-[80px]" style={{ color: '#1f2937' }}>{receiptData.collected_by}</div>
                </div>
             </div>
          </div>
          
          <div className="border-t border-dashed my-4" style={{ borderColor: '#d1d5db' }}></div>

          {/* Footer Text */}
          <div className="text-center mb-6">
            <h4 className="font-serif italic text-lg mb-1" style={{ color: '#6b21a8' }}>Thank you for your payment!</h4>
            <p className="text-[10px]" style={{ color: '#6b7280' }}>This is a digital payment acknowledgement.</p>
          </div>
        </div>
        
        {/* Footer Bar */}
        <div className="py-3 px-4 flex justify-between items-center mt-auto" style={{ backgroundColor: '#faf5ff' }}>
          <div className="flex items-center gap-1 text-[10px] font-medium" style={{ color: '#7e22ce' }}>
            <ShieldCheck size={12} color="#7e22ce" />
            Secure
          </div>
          <div className="w-1 h-1 rounded-full" style={{ backgroundColor: '#d8b4fe' }}></div>
          <div className="flex items-center gap-1 text-[10px] font-medium" style={{ color: '#7e22ce' }}>
            <ShieldCheck size={12} color="#7e22ce" />
            Transparent
          </div>
          <div className="w-1 h-1 rounded-full" style={{ backgroundColor: '#d8b4fe' }}></div>
          <div className="flex items-center gap-1 text-[10px] font-medium" style={{ color: '#7e22ce' }}>
            <ShieldCheck size={12} color="#7e22ce" />
            Reliable
          </div>
        </div>
      </div>
    </div>
  );
};

