import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Users, FileText, ClipboardList, TrendingUp } from 'lucide-react';
import CourseManager from '../components/CourseManager';
import AssignmentManager from '../components/AssignmentManager';
import DocumentUpload from '../components/DocumentUpload';
import api from '../services/api';

function FacultyDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => api.get('/auth/me').then(res => res.data),
  });

  const { data: stats } = useQuery({
    queryKey: ['userStats'],
    queryFn: () => api.get('/statistics/user').then(res => res.data),
  });

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome, {user?.full_name || 'Faculty'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your courses and students
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
            onClick={() => setActiveTab('courses')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'courses'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Courses
          </button>
          <button
            onClick={() => setActiveTab('assignments')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'assignments'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Assignments
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
        </div>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <BookOpen className="text-blue-600 dark:text-blue-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Courses Taught</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.courses_taught || 0}</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Active courses</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <Users className="text-green-600 dark:text-green-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Students</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Total enrolled</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="text-purple-600 dark:text-purple-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Documents</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Uploaded materials</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <ClipboardList className="text-orange-600 dark:text-orange-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Assignments</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Total assignments</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="text-teal-600 dark:text-teal-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Performance</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0%</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Average score</p>
            </div>
          </div>
        )}

        {activeTab === 'courses' && (
          <CourseManager />
        )}

        {activeTab === 'assignments' && (
          <AssignmentManager userRole={user?.role} />
        )}

        {activeTab === 'documents' && (
          <DocumentUpload userRole={user?.role} />
        )}
      </div>
    </div>
  );
}

export default FacultyDashboard;
