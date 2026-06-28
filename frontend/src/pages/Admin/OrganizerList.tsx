import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../core/api';
import toast from 'react-hot-toast';
import { PlusCircle, Search, Power } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface Organizer {
  id: string;
  organizer_code: string;
  name: string;
  mobile: string;
  is_active: boolean;
  created_at: string;
}

export const OrganizerList = () => {
  const { t } = useTranslation(['collections']);

  const navigate = useNavigate();
  const [organizers, setOrganizers] = useState<Organizer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchOrganizers = async () => {
    try {
      const response = await api.get('/organizers');
      setOrganizers(response.data.items);
    } catch (error) {
      toast.error('Failed to load organizers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrganizers();
  }, []);

  const toggleStatus = async (id: string, currentStatus: boolean) => {
    if (!window.confirm(`Are you sure you want to ${currentStatus ? 'deactivate' : 'activate'} this organizer?`)) return;
    
    try {
      await api.patch(`/organizers/${id}/status`, { is_active: !currentStatus });
      toast.success(`Organizer ${currentStatus ? 'deactivated' : 'activated'} successfully`);
      fetchOrganizers();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const filtered = organizers.filter(o => 
    o.name.toLowerCase().includes(search.toLowerCase()) || 
    o.mobile.includes(search) ||
    o.organizer_code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Organizers</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Manage all chit fund organizers in the system</p>
        </div>
        <button 
          onClick={() => navigate('/admin/organizers/new')}
          className="flex items-center justify-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <PlusCircle size={20} />
          <span>Add Organizer</span>
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-100 dark:border-gray-700">
          <div className="relative max-w-md">
            <input 
              type="text" 
              placeholder="Search by name, code or mobile..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 outline-none"
            />
            <Search className="absolute left-3 top-2.5 text-gray-400" size={20} />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 dark:bg-gray-900 text-gray-500 dark:text-gray-400 text-sm">
                <th className="p-4 font-medium">Code</th>
                <th className="p-4 font-medium">Name</th>
                <th className="p-4 font-medium">Mobile</th>
                <th className="p-4 font-medium">{t('collections:collections_status')}</th>
                <th className="p-4 font-medium text-right">{t('collections:collections_action')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-gray-500">Loading organizers...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-gray-500">No organizers found.</td>
                </tr>
              ) : (
                filtered.map(org => (
                  <tr key={org.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                    <td className="p-4 text-sm font-medium text-gray-900 dark:text-white">{org.organizer_code}</td>
                    <td className="p-4 text-sm text-gray-700 dark:text-gray-300">{org.name}</td>
                    <td className="p-4 text-sm text-gray-700 dark:text-gray-300">{org.mobile}</td>
                    <td className="p-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        org.is_active 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                      }`}>
                        {org.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <button 
                        onClick={() => toggleStatus(org.id, org.is_active)}
                        className={`p-2 rounded-lg transition-colors ${
                          org.is_active 
                            ? 'text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20' 
                            : 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20'
                        }`}
                        title={org.is_active ? 'Deactivate' : 'Activate'}
                      >
                        <Power size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
