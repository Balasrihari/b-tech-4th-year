import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, TrendingUp, Clock, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import api from '../services/api';

const StudentMonitoring = () => {
  const [selectedCourse, setSelectedCourse] = useState('');
  const [expandedStudent, setExpandedStudent] = useState(null);

  // Fetch courses for dropdown
  const { data: courses = [] } = useQuery({
    queryKey: ['courses'],
    queryFn: () => api.get('/courses').then(res => res.data),
  });

  // Fetch students
  const { data: students = [], isLoading: studentsLoading } = useQuery({
    queryKey: ['faculty-students', selectedCourse],
    queryFn: () => api.get('/faculty/students', {
      params: selectedCourse ? { course_id: selectedCourse } : {}
    }).then(res => res.data),
  });

  // Fetch student performance
  const { data: performances = [], isLoading: performanceLoading } = useQuery({
    queryKey: ['faculty-students-performance', selectedCourse],
    queryFn: () => api.get('/faculty/students/performance', {
      params: selectedCourse ? { course_id: selectedCourse } : {}
    }).then(res => res.data),
  });

  // Fetch course progress
  const { data: courseProgress = [] } = useQuery({
    queryKey: ['faculty-courses-progress'],
    queryFn: () => api.get('/faculty/courses/progress').then(res => res.data),
  });

  // Fetch detailed student progress
  const { data: studentDetail } = useQuery({
    queryKey: ['faculty-student-detail', expandedStudent],
    queryFn: () => api.get(`/faculty/students/${expandedStudent}/progress`).then(res => res.data),
    enabled: !!expandedStudent,
  });

  const isLoading = studentsLoading || performanceLoading;

  const formatTime = (minutes) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getMasteryColor = (mastery) => {
    if (mastery >= 0.8) return 'bg-green-500';
    if (mastery >= 0.5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Student Monitoring</h2>
      </div>

      {/* Course Progress Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {courseProgress.map((course) => (
          <div key={course.course_id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <BookOpen size={20} className="text-blue-600 dark:text-blue-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white">{course.course_name}</h3>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Total Students:</span>
                <span className="font-medium text-gray-900 dark:text-white">{course.total_students}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Active:</span>
                <span className="font-medium text-green-600 dark:text-green-400">{course.active_students}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Avg Mastery:</span>
                <span className="font-medium text-gray-900 dark:text-white">{(course.average_mastery * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Total Time:</span>
                <span className="font-medium text-gray-900 dark:text-white">{course.total_time_spent_hours.toFixed(1)}h</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Course Filter */}
      <div>
        <select
          value={selectedCourse}
          onChange={(e) => setSelectedCourse(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option value="">All Courses</option>
          {courses.map((course) => (
            <option key={course.id} value={course.id}>
              {course.code} - {course.title}
            </option>
          ))}
        </select>
      </div>

      {/* Students List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading student data...</div>
        </div>
      ) : (
        <div className="space-y-4">
          {performances.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <p className="text-lg">No students found</p>
              <p className="text-sm">Students will appear here once they enroll in your courses</p>
            </div>
          ) : (
            performances.map((performance) => (
              <div
                key={`${performance.student_id}-${performance.course_id}`}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <Users size={20} className="text-blue-600 dark:text-blue-400" />
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {performance.student_name}
                        </h3>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          ({performance.student_email})
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        Course: {performance.course_name}
                      </p>
                      
                      {/* Performance Metrics */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <TrendingUp size={16} className="text-purple-600 dark:text-purple-400" />
                            <span className="text-xs text-gray-600 dark:text-gray-400">Quiz Avg</span>
                          </div>
                          <p className={`text-lg font-bold ${getPerformanceColor(performance.average_quiz_score)}`}>
                            {performance.average_quiz_score.toFixed(1)}%
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {performance.total_quizzes_taken} attempts
                          </p>
                        </div>

                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <BookOpen size={16} className="text-green-600 dark:text-green-400" />
                            <span className="text-xs text-gray-600 dark:text-gray-400">Assignment Avg</span>
                          </div>
                          <p className={`text-lg font-bold ${getPerformanceColor(performance.average_assignment_score)}`}>
                            {performance.average_assignment_score.toFixed(1)}%
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {performance.total_assignments_submitted} submitted
                          </p>
                        </div>

                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <TrendingUp size={16} className="text-blue-600 dark:text-blue-400" />
                            <span className="text-xs text-gray-600 dark:text-gray-400">Mastery</span>
                          </div>
                          <p className={`text-lg font-bold ${getPerformanceColor(performance.total_mastery_level * 100)}`}>
                            {(performance.total_mastery_level * 100).toFixed(1)}%
                          </p>
                          <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 mt-1">
                            <div
                              className={`h-2 rounded-full ${getMasteryColor(performance.total_mastery_level)}`}
                              style={{ width: `${performance.total_mastery_level * 100}%` }}
                            />
                          </div>
                        </div>

                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <Clock size={16} className="text-orange-600 dark:text-orange-400" />
                            <span className="text-xs text-gray-600 dark:text-gray-400">Time Spent</span>
                          </div>
                          <p className="text-lg font-bold text-gray-900 dark:text-white">
                            {formatTime(performance.total_time_spent_minutes)}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {performance.last_activity
                              ? `Active: ${new Date(performance.last_activity).toLocaleDateString()}`
                              : 'No recent activity'
                            }
                          </p>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => setExpandedStudent(
                        expandedStudent === performance.student_id ? null : performance.student_id
                      )}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors dark:text-gray-400 dark:hover:text-blue-400 dark:hover:bg-blue-900/20"
                    >
                      {expandedStudent === performance.student_id ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </button>
                  </div>
                </div>

                {/* Expanded Detail View */}
                {expandedStudent === performance.student_id && studentDetail && (
                  <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-700/50">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Detailed Progress</h4>
                    
                    {/* Learning Progress */}
                    <div className="mb-6">
                      <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Learning Progress</h5>
                      <div className="space-y-2">
                        {studentDetail.learning_progress?.length > 0 ? (
                          studentDetail.learning_progress.map((progress, idx) => (
                            <div key={idx} className="flex items-center justify-between bg-white dark:bg-gray-800 rounded p-2">
                              <span className="text-sm text-gray-700 dark:text-gray-300">{progress.topic}</span>
                              <div className="flex items-center gap-4">
                                <div className="w-24 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${getMasteryColor(progress.mastery_level)}`}
                                    style={{ width: `${progress.mastery_level * 100}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  {formatTime(progress.time_spent_minutes)}
                                </span>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-gray-500 dark:text-gray-400">No learning progress recorded</p>
                        )}
                      </div>
                    </div>

                    {/* Quiz Performance */}
                    <div className="mb-6">
                      <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recent Quiz Attempts</h5>
                      {studentDetail.quiz_performance?.recent_attempts?.length > 0 ? (
                        <div className="space-y-2">
                          {studentDetail.quiz_performance.recent_attempts.map((attempt, idx) => (
                            <div key={idx} className="flex items-center justify-between bg-white dark:bg-gray-800 rounded p-2">
                              <span className="text-sm text-gray-700 dark:text-gray-300">Quiz #{attempt.quiz_id}</span>
                              <span className={`text-sm font-medium ${getPerformanceColor(attempt.score)}`}>
                                {attempt.score.toFixed(1)}%
                              </span>
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {new Date(attempt.completed_at).toLocaleDateString()}
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 dark:text-gray-400">No quiz attempts recorded</p>
                      )}
                    </div>

                    {/* Assignment Performance */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recent Submissions</h5>
                      {studentDetail.assignment_performance?.recent_submissions?.length > 0 ? (
                        <div className="space-y-2">
                          {studentDetail.assignment_performance.recent_submissions.map((submission, idx) => (
                            <div key={idx} className="flex items-center justify-between bg-white dark:bg-gray-800 rounded p-2">
                              <span className="text-sm text-gray-700 dark:text-gray-300">Assignment #{submission.assignment_id}</span>
                              <span className={`text-sm font-medium ${getPerformanceColor(submission.score || 0)}`}>
                                {submission.score ? `${submission.score.toFixed(1)}%` : 'Not graded'}
                              </span>
                              <span className={`text-xs px-2 py-1 rounded ${
                                submission.status === 'graded' 
                                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                              }`}>
                                {submission.status}
                              </span>
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {new Date(submission.submitted_at).toLocaleDateString()}
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 dark:text-gray-400">No submissions recorded</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default StudentMonitoring;
