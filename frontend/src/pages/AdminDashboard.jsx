import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, Shield, BarChart3 } from 'lucide-react';
import UserManager from '../components/UserManager';
import SystemStatistics from '../components/SystemStatistics';
import AuditLogViewer from '../components/AuditLogViewer';
import RoleManager from '../components/RoleManager';
import DocumentStatistics from '../components/DocumentStatistics';
import AIUsageStatistics from '../components/AIUsageStatistics';
import api from '../services/api';

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => api.get('/auth/me').then(res => res.data),
  });

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome, {user?.full_name || 'Administrator'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            System administration and management
          </p>
        </div>

        <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'overview'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'users'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('statistics')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'statistics'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'documents'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Documents
          </button>
          <button
            onClick={() => setActiveTab('ai-usage')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'ai-usage'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            AI Usage
          </button>
          <button
            onClick={() => setActiveTab('audit-logs')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'audit-logs'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Audit Logs
          </button>
          <button
            onClick={() => setActiveTab('roles')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'roles'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Roles
          </button>
        </div>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <Users className="text-blue-600 dark:text-blue-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">User Management</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400">Manage system users, roles, and permissions</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="text-green-600 dark:text-green-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Role Management</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400">Configure user roles and access control</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <BarChart3 className="text-purple-600 dark:text-purple-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">System Statistics</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400">View system-wide usage and metrics</p>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <UserManager />
        )}

        {activeTab === 'statistics' && (
          <SystemStatistics />
        )}

        {activeTab === 'documents' && (
          <DocumentStatistics />
        )}

        {activeTab === 'ai-usage' && (
          <AIUsageStatistics />
        )}

        {activeTab === 'audit-logs' && (
          <AuditLogViewer userRole={user?.role} />
        )}

        {activeTab === 'roles' && (
          <RoleManager userRole={user?.role} />
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;
