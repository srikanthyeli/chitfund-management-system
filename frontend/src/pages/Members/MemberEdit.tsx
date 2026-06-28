import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save, User, Phone, Mail, MapPin, Hash, BookOpen } from 'lucide-react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import api from '../../core/api';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';

export const MemberEdit: React.FC = () => {
  const { t } = useTranslation(['common', 'organisers', 'auth']);

  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [formData, setFormData] = useState({
    full_name: '',
    mobile: '', // Read-only
    alternate_mobile: '',
    email: '',
    address: '',
    village: '',
    mandal: '',
    district: '',
    state: '',
    pincode: '',
    aadhaar_last4: '',
    notes: '',
  });

  useEffect(() => {
    const fetchMember = async () => {
      try {
        const response = await api.get(`/members/${id}`);
        const m = response.data;
        setFormData({
          full_name: m.full_name || '',
          mobile: m.mobile || '',
          alternate_mobile: m.alternate_mobile || '',
          email: m.email || '',
          address: m.address || '',
          village: m.village || '',
          mandal: m.mandal || '',
          district: m.district || '',
          state: m.state || '',
          pincode: m.pincode || '',
          aadhaar_last4: m.aadhaar_last4 || '',
          notes: m.notes || '',
        });
      } catch (error: any) {
        toast.error('Failed to load member profile');
        navigate('/organizer/members');
      } finally {
        setFetching(false);
      }
    };
    fetchMember();
  }, [id, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validate = (): boolean => {
    // Validate alternate mobile if supplied
    if (formData.alternate_mobile) {
      const cleanAlt = formData.alternate_mobile.replace(/[\s\-()]/g, '').replace(/^(\+91|91|0)/, '');
      if (!/^[6-9]\d{9}$/.test(cleanAlt)) {
        toast.error('Please enter a valid 10-digit Indian alternate mobile number');
        return false;
      }
    }

    // Validate pincode if supplied
    if (formData.pincode && !/^\d{6}$/.test(formData.pincode)) {
      toast.error('Pincode must be exactly 6 digits');
      return false;
    }

    // Validate Aadhaar last 4 if supplied
    if (formData.aadhaar_last4 && !/^\d{4}$/.test(formData.aadhaar_last4)) {
      toast.error('Aadhaar last 4 must be exactly 4 digits');
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
        full_name: formData.full_name,
        alternate_mobile: formData.alternate_mobile || null,
        email: formData.email || null,
        address: formData.address || null,
        village: formData.village || null,
        mandal: formData.mandal || null,
        district: formData.district || null,
        state: formData.state || null,
        pincode: formData.pincode || null,
        aadhaar_last4: formData.aadhaar_last4 || null,
        notes: formData.notes || null,
      };

      await api.put(`/members/${id}`, payload);
      toast.success('Member profile updated successfully!');
      navigate(`/organizer/members/${id}`);
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to update member profile');
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return <div className="flex justify-center p-8">Loading member profile...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto pb-12">
      <div className="flex items-center space-x-3 mb-6">
        <Link to={`/organizer/members/${id}`} className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-600 dark:text-slate-400">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white">Edit Member Profile</h1>
          <p className="text-sm text-slate-500">Update personal and address details</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-slate-100 dark:border-gray-700 p-6 space-y-6">
        
        {/* Profile Info Section */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider border-b pb-1">Personal Details</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Full Name <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <User size={16} />
                </span>
                <input
                  type="text"
                  name="full_name"
                  required
                  placeholder="e.g. Ramesh Kumar"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Aadhaar Last 4 Digits
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Hash size={16} />
                </span>
                <input
                  type="text"
                  name="aadhaar_last4"
                  maxLength={4}
                  placeholder="e.g. 5678"
                  value={formData.aadhaar_last4}
                  onChange={handleChange}
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Mobile Number (Read-only)
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Phone size={16} />
                </span>
                <input
                  type="text"
                  name="mobile"
                  disabled
                  value={formData.mobile}
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 text-gray-500 cursor-not-allowed text-sm focus:outline-none"
                />
              </div>
              <p className="text-[11px] text-slate-400 mt-1">To change mobile number, use the action on the member profile page.</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Alternate Mobile
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Phone size={16} />
                </span>
                <input
                  type="text"
                  name="alternate_mobile"
                  placeholder="e.g. 9988776655"
                  value={formData.alternate_mobile}
                  onChange={handleChange}
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">{t('auth:login_email')}</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                <Mail size={16} />
              </span>
              <input
                type="email"
                name="email"
                placeholder="e.g. name@example.com"
                value={formData.email}
                onChange={handleChange}
                className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Address Info Section */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider border-b pb-1">Address Details</h3>
          
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              House/Street Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-start pt-3 pl-3 text-slate-400">
                <MapPin size={16} />
              </span>
              <textarea
                name="address"
                rows={2}
                placeholder="Street address, flat no, etc."
                value={formData.address}
                onChange={handleChange}
                className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Village / Area
              </label>
              <input
                type="text"
                name="village"
                placeholder="Village name"
                value={formData.village}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                Mandal / Sub-district
              </label>
              <input
                type="text"
                name="mandal"
                placeholder="Mandal name"
                value={formData.mandal}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                District
              </label>
              <input
                type="text"
                name="district"
                placeholder="District name"
                value={formData.district}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">{t('organisers:organisers_state')}</label>
              <input
                type="text"
                name="state"
                placeholder="State name"
                value={formData.state}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              Pincode
            </label>
            <input
              type="text"
              name="pincode"
              maxLength={6}
              placeholder="e.g. 500032"
              value={formData.pincode}
              onChange={handleChange}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
        </div>

        {/* Other Info */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider border-b pb-1">Additional Notes</h3>
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
              Internal Remarks
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-start pt-3 pl-3 text-slate-400">
                <BookOpen size={16} />
              </span>
              <textarea
                name="notes"
                rows={3}
                placeholder="Any remarks..."
                value={formData.notes}
                onChange={handleChange}
                className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
              />
            </div>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="flex space-x-4 pt-4 border-t border-slate-100 dark:border-gray-700">
          <Link
            to={`/organizer/members/${id}`}
            className="flex-1 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-slate-700 dark:text-gray-300 font-medium text-sm text-center transition-colors"
          >{t('common:cancel')}</Link>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-medium text-sm flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
          >
            <Save size={18} />
            <span>{loading ? 'Saving...' : 'Save Changes'}</span>
          </button>
        </div>

      </form>
    </div>
  );
};
