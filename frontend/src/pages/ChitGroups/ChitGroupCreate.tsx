import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save, Briefcase, Calendar, Percent, ShieldAlert } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../core/api';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';

export const ChitGroupCreate: React.FC = () => {
  const { t } = useTranslation(['chitGroups', 'common']);

  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const getNextMonthFirstDayStr = () => {
    const d = new Date();
    const nextMonth = new Date(d.getFullYear(), d.getMonth() + 1, 1);
    const y = nextMonth.getFullYear();
    const m = String(nextMonth.getMonth() + 1).padStart(2, '0');
    return `${y}-${m}-01`;
  };

  const [formData, setFormData] = useState({
    chit_name: '',
    description: '',
    total_shares: '20',
    duration_months: '20',
    monthly_installment_per_share: '',
    total_chit_value: '0',
    maintenance_charge: '0',
    maintenance_charge_type: 'FIXED' as 'FIXED' | 'PERCENTAGE',
    start_date: getNextMonthFirstDayStr(),
    installment_due_day: '1',
  });

  // Keep duration equal to total shares by default
  useEffect(() => {
    if (formData.total_shares) {
      setFormData((prev) => ({ ...prev, duration_months: prev.total_shares }));
    }
  }, [formData.total_shares]);

  // Keep total chit value calculated automatically
  useEffect(() => {
    const installment = parseFloat(formData.monthly_installment_per_share) || 0;
    const shares = parseInt(formData.total_shares) || 0;
    setFormData((prev) => ({ ...prev, total_chit_value: (installment * shares).toString() }));
  }, [formData.monthly_installment_per_share, formData.total_shares]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validate = (): boolean => {
    const nameTrimmed = formData.chit_name.trim();
    if (nameTrimmed.length < 2 || nameTrimmed.length > 150) {
      toast.error('Chit group name must be between 2 and 150 characters');
      return false;
    }

    const shares = parseInt(formData.total_shares) || 0;
    if (shares < 2) {
      toast.error('Total shares must be at least 2');
      return false;
    }

    const duration = parseInt(formData.duration_months) || 0;
    if (duration !== shares) {
      toast.error('Duration in months must equal total shares');
      return false;
    }

    const installment = parseFloat(formData.monthly_installment_per_share) || 0;
    if (installment <= 0) {
      toast.error('Monthly installment per share must be greater than zero');
      return false;
    }

    const totalVal = parseFloat(formData.total_chit_value) || 0;
    if (totalVal !== installment * shares) {
      toast.error('Total chit value must equal monthly installment multiplied by total shares');
      return false;
    }

    const maintenance = parseFloat(formData.maintenance_charge) || 0;
    if (maintenance < 0) {
      toast.error('Maintenance charge cannot be negative');
      return false;
    }

    if (formData.maintenance_charge_type === 'PERCENTAGE' && maintenance > 100) {
      toast.error('Percentage maintenance charge cannot exceed 100%');
      return false;
    }

    const dueDay = parseInt(formData.installment_due_day) || 0;
    if (dueDay < 1 || dueDay > 28) {
      toast.error('Installment due day must be between 1 and 28');
      return false;
    }

    // Validate start date is the 1st of a month
    const parts = formData.start_date.split('-');
    if (parts.length !== 3 || parts[2] !== '01') {
      toast.error('Start date must be the 1st day of a month (e.g. YYYY-MM-01)');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const payload = {
        chit_name: formData.chit_name.trim(),
        description: formData.description.trim() || null,
        total_shares: parseInt(formData.total_shares),
        duration_months: parseInt(formData.duration_months),
        monthly_installment_per_share: parseFloat(formData.monthly_installment_per_share),
        total_chit_value: parseFloat(formData.total_chit_value),
        maintenance_charge: parseFloat(formData.maintenance_charge),
        maintenance_charge_type: formData.maintenance_charge_type,
        start_date: formData.start_date,
        installment_due_day: parseInt(formData.installment_due_day),
      };

      await api.post('/chit-groups', payload);
      toast.success('Chit group created successfully!');
      navigate('/organizer/chit-groups');
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to create chit group');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto pb-12">
      <div className="flex items-center space-x-3 mb-6">
        <Link to="/organizer/chit-groups" className="p-2 hover:bg-slate-100 dark:hover:bg-gray-800 rounded-full transition-colors text-slate-600 dark:text-slate-400">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white">{t('chitGroups:chitgroups_create')}</h1>
          <p className="text-sm text-slate-500">Configure financials and set up a new chit fund</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-slate-100 dark:border-gray-700 p-6 space-y-6">
        
        {/* Core Details */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider border-b pb-1">Group Details</h3>
          
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              Chit Group Name <span className="text-rose-500">*</span>
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                <Briefcase size={16} />
              </span>
              <input
                type="text"
                name="chit_name"
                required
                placeholder="e.g. Lakhpati Scheme Jan 2026"
                value={formData.chit_name}
                onChange={handleChange}
                className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              Description / Notes
            </label>
            <textarea
              name="description"
              rows={2}
              placeholder="Provide a brief summary or terms of the group..."
              value={formData.description}
              onChange={handleChange}
              className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
            />
          </div>
        </div>

        {/* Financial Configurations */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider border-b pb-1">Financial Configurations</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Total Shares <span className="text-rose-500">*</span>
              </label>
              <input
                type="number"
                name="total_shares"
                required
                min="2"
                value={formData.total_shares}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">{t('chitGroups:chitgroups_duration')}<span className="text-slate-400">(Calculated)</span>
              </label>
              <input
                type="text"
                name="duration_months"
                disabled
                value={formData.duration_months}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-gray-950 text-slate-500 text-sm cursor-not-allowed"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Monthly Installment per Share (₹) <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400 text-sm">
                  ₹
                </span>
                <input
                  type="number"
                  name="monthly_installment_per_share"
                  required
                  placeholder="e.g. 5000"
                  value={formData.monthly_installment_per_share}
                  onChange={handleChange}
                  className="w-full pl-7 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Total Chit Value (₹) <span className="text-slate-400">(Calculated)</span>
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500 text-sm">
                  ₹
                </span>
                <input
                  type="text"
                  name="total_chit_value"
                  disabled
                  value={Number(formData.total_chit_value).toLocaleString('en-IN')}
                  className="w-full pl-7 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-gray-950 text-slate-600 font-bold text-sm cursor-not-allowed"
                />
              </div>
            </div>
          </div>

          {/* Maintenance Charges */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Organizer Commission Type
              </label>
              <select
                name="maintenance_charge_type"
                value={formData.maintenance_charge_type}
                onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              >
                <option value="FIXED">Fixed Amount (₹)</option>
                <option value="PERCENTAGE">Percentage (%)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Organizer Commission / Fee
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  {formData.maintenance_charge_type === 'FIXED' ? '₹' : <Percent size={14} />}
                </span>
                <input
                  type="number"
                  name="maintenance_charge"
                  placeholder="e.g. 500"
                  value={formData.maintenance_charge}
                  onChange={handleChange}
                  className="w-full pl-8 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Schedule */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider border-b pb-1">Timeline & Schedule</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">{t('chitGroups:chitgroups_start_date')}<span className="text-rose-500">*</span> <span className="text-slate-400 text-[10px]">(Must be 1st day of month)</span>
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Calendar size={16} />
                </span>
                <input
                  type="date"
                  name="start_date"
                  required
                  value={formData.start_date}
                  onChange={handleChange}
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Monthly Due Day of Month <span className="text-rose-500">*</span>
              </label>
              <input
                type="number"
                name="installment_due_day"
                required
                min="1"
                max="28"
                value={formData.installment_due_day}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Important Warning Alert */}
        <div className="p-3 bg-amber-50 dark:bg-amber-950/20 text-amber-800 dark:text-amber-300 rounded-xl flex items-start space-x-2 text-xs">
          <ShieldAlert size={16} className="shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Financial Settings Lock</p>
            <p className="mt-0.5">Configurations are locked once you start allocating member shares. Once the chit becomes ACTIVE, details cannot be changed.</p>
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex space-x-4 pt-4 border-t border-slate-100 dark:border-gray-700">
          <Link
            to="/organizer/chit-groups"
            className="flex-1 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-slate-700 dark:text-gray-300 font-medium text-sm text-center transition-colors"
          >{t('common:cancel')}</Link>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-medium text-sm flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
          >
            <Save size={18} />
            <span>{loading ? 'Creating...' : 'Create Chit Group'}</span>
          </button>
        </div>

      </form>
    </div>
  );
};
