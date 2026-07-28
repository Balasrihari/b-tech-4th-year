import { useQuery } from '@tanstack/react-query';
import { statisticsService } from '../services/statistics';
import { Users, BookOpen, FileText, ClipboardList, Brain, CheckSquare, UserCheck } from 'lucide-react';

export default function SystemStatistics() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['systemStats'],
    queryFn: statisticsService.getSystem,
  });

  if (isLoading) return <div>Loading statistics...</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Users className="text-blue-600 dark:text-blue-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Total Users</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.users?.total || 0}</p>
          <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex justify-between">
              <span>Students: {stats?.users?.students || 0}</span>
              <span>Faculty: {stats?.users?.faculty || 0}</span>
              <span>Admins: {stats?.users?.admins || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <BookOpen className="text-green-600 dark:text-green-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Courses</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.courses || 0}</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Active courses</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="text-purple-600 dark:text-purple-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Documents</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.documents || 0}</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Uploaded documents</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <ClipboardList className="text-orange-600 dark:text-orange-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Assignments</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.assignments || 0}</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Total assignments</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="text-teal-600 dark:text-teal-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Quizzes</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.quizzes || 0}</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Available quizzes</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <CheckSquare className="text-pink-600 dark:text-pink-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Tasks</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.todos || 0}</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Total tasks</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <UserCheck className="text-indigo-600 dark:text-indigo-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Enrollments</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.enrollments || 0}</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Course enrollments</p>
        </div>
      </div>
    </div>
  );
}
