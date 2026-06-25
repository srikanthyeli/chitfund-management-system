import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Briefcase, ArrowLeft } from 'lucide-react';

export const MyChitDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center mb-4">
        <Link to="/member/chits" className="mr-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <Briefcase className="w-6 h-6 mr-2 text-purple-600" /> Chit Details
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">ID: {id}</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-200 dark:border-gray-700 shadow-sm">
        <Briefcase className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Under Construction</h3>
        <p className="text-gray-500 mt-2">The detailed view for this chit group will be available soon.</p>
        <p className="text-sm text-gray-400 mt-4">We will implement the transaction history and full auction details here.</p>
      </div>
    </div>
  );
};
