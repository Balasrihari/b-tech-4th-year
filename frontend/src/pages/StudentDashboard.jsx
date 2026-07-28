import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, FileText, Brain, Calendar, CheckSquare, TrendingUp, Layers, Award, BarChart3 } from 'lucide-react';
import TodoList from '../components/TodoList';
import FlashcardManager from '../components/FlashcardManager';
import QuizManager from '../components/QuizManager';
import LearningAnalytics from '../components/LearningAnalytics';
import StudyPlanner from '../components/StudyPlanner';
import NoteManager from '../components/NoteManager';
import StudentAssignments from '../components/StudentAssignments';
import DocumentUpload from '../components/DocumentUpload';
import api from '../services/api';

function StudentDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => api.get('/auth/me').then(res => res.data),
  });

  const { data: courses } = useQuery({
    queryKey: ['courses'],
    queryFn: () => api.get('/courses/').then(res => res.data),
  });

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome, {user?.full_name || 'Student'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your learning journey
          </p>
        </div>

        <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'overview'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('tasks')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'tasks'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Tasks
          </button>
          <button
            onClick={() => setActiveTab('flashcards')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'flashcards'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Flashcards
          </button>
          <button
            onClick={() => setActiveTab('quizzes')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'quizzes'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Quizzes
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'analytics'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Analytics
          </button>
          <button
            onClick={() => setActiveTab('planner')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'planner'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Study Planner
          </button>
          <button
            onClick={() => setActiveTab('courses')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'courses'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Courses
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'notes'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Notes
          </button>
          <button
            onClick={() => setActiveTab('assignments')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
              activeTab === 'assignments'
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Assignments
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`px-4 py-2 font-medium whitespace-nowrap ${
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
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Enrolled Courses</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{courses?.length || 0}</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Active enrollments</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="text-green-600 dark:text-green-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Documents</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Uploaded documents</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="text-purple-600 dark:text-purple-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI Questions</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Questions asked</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <CheckSquare className="text-orange-600 dark:text-orange-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Tasks</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Pending tasks</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="text-teal-600 dark:text-teal-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Progress</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0%</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Overall completion</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-4">
                <Calendar className="text-pink-600 dark:text-pink-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Study Time</h3>
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">0h</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">This week</p>
            </div>
          </div>
        )}

        {activeTab === 'tasks' && (
          <TodoList />
        )}

        {activeTab === 'flashcards' && (
          <FlashcardManager />
        )}

        {activeTab === 'quizzes' && (
          <QuizManager />
        )}

        {activeTab === 'analytics' && (
          <LearningAnalytics />
        )}

        {activeTab === 'planner' && (
          <StudyPlanner />
        )}

        {activeTab === 'courses' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">My Courses</h2>
            {courses && courses.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {courses.map((course) => (
                  <div key={course.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <h3 className="font-semibold text-gray-900 dark:text-white">{course.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{course.code}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{course.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No courses enrolled yet.</p>
            )}
          </div>
        )}

        {activeTab === 'notes' && (
          <NoteManager />
        )}

        {activeTab === 'assignments' && (
          <StudentAssignments />
        )}

        {activeTab === 'documents' && (
          <DocumentUpload userRole={user?.role} />
        )}
      </div>
    </div>
  );
}

export default StudentDashboard;
