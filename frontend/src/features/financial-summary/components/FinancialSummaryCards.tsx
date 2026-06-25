import React from 'react';
import { 
    IndianRupee, 
    TrendingUp, 
    AlertCircle, 
    CheckCircle2, 
    Wallet, 
    PiggyBank,
    Building2,
    PieChart
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper to format currency
const formatCurrency = (amount: number | string) => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(Number(amount));
};

interface FinancialSummaryCardsProps {
    data: any;
    isLoading?: boolean;
}

const SummaryCard = ({ title, amount, icon: Icon, colorClass, subtitle }: any) => (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col hover:shadow-md transition-shadow">
        <div className="flex justify-between items-start mb-4">
            <h3 className="text-slate-500 font-medium text-sm">{title}</h3>
            <div className={twMerge("p-2 rounded-lg", colorClass)}>
                <Icon size={20} />
            </div>
        </div>
        <div className="flex-1">
            <h2 className="text-2xl font-bold text-slate-800">{formatCurrency(amount)}</h2>
            {subtitle && (
                <p className="text-xs text-slate-400 mt-2">{subtitle}</p>
            )}
        </div>
    </div>
);

export const FinancialSummaryCards: React.FC<FinancialSummaryCardsProps> = ({ data, isLoading }) => {
    if (isLoading || !data) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[...Array(8)].map((_, i) => (
                    <div key={i} className="bg-white rounded-xl border border-slate-200 p-6 h-36 animate-pulse">
                        <div className="h-4 bg-slate-200 rounded w-1/2 mb-4"></div>
                        <div className="h-8 bg-slate-200 rounded w-3/4"></div>
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <SummaryCard 
                title="Operational Cash Position" 
                amount={data.net_cash_position} 
                icon={Wallet} 
                colorClass="bg-purple-100 text-purple-600"
                subtitle="Net cash currently available"
            />
            <SummaryCard 
                title="Total Collection" 
                amount={data.total_collection} 
                icon={TrendingUp} 
                colorClass="bg-emerald-100 text-emerald-600"
                subtitle="Successfully received payments"
            />
            <SummaryCard 
                title="Pending Collection" 
                amount={data.pending_collection} 
                icon={AlertCircle} 
                colorClass="bg-amber-100 text-amber-600"
                subtitle="Expected but not yet paid"
            />
            <SummaryCard 
                title="Overdue Amount" 
                amount={data.overdue_amount} 
                icon={AlertCircle} 
                colorClass="bg-red-100 text-red-600"
                subtitle="Past grace period end date"
            />
            
            <SummaryCard 
                title="Winner Payouts Paid" 
                amount={data.winner_payouts_paid} 
                icon={CheckCircle2} 
                colorClass="bg-blue-100 text-blue-600"
                subtitle="Successfully paid to winners"
            />
            <SummaryCard 
                title="Pending Winner Payouts" 
                amount={data.pending_winner_payouts} 
                icon={PiggyBank} 
                colorClass="bg-orange-100 text-orange-600"
                subtitle="Draft or pending payment status"
            />
            <SummaryCard 
                title="Commission Earned" 
                amount={data.organizer_commission_earned} 
                icon={IndianRupee} 
                colorClass="bg-indigo-100 text-indigo-600"
                subtitle="From finalized auctions"
            />
            <SummaryCard 
                title="Dividends Distributed" 
                amount={data.dividends_distributed} 
                icon={PieChart} 
                colorClass="bg-teal-100 text-teal-600"
                subtitle="Credited to active members"
            />
        </div>
    );
};
