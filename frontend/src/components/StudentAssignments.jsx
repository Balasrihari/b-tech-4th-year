import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assignmentsService } from '../services/assignments';
import { FileText, Clock, Send, CheckCircle, AlertCircle } from 'lucide-react';

const StudentAssignments = () => {
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [submissionContent, setSubmissionContent] = useState('');
  const [showSubmitForm, setShowSubmitForm] = useState(false);

  const queryClient = useQueryClient();

  // Fetch available assignments
  const { data: assignments = [], isLoading: assignmentsLoading } = useQuery({
    queryKey: ['assignments'],
    queryFn: () => assignmentsService.getAll(),
  });

  // Fetch my submissions
  const { data: mySubmissions = [], isLoading: submissionsLoading } = useQuery({
    queryKey: ['my-submissions'],
    queryFn: () => assignmentsService.getMySubmissions(),
  });

  // Submit assignment mutation
  const submitMutation = useMutation({
    mutationFn: ({ assignmentId, data }) => assignmentsService.submit(assignmentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['my-submissions']);
      queryClient.invalidateQueries(['assignments']);
      setShowSubmitForm(false);
      setSubmissionContent('');
      setSelectedAssignment(null);
    },
  });

  const handleSubmit = () => {
    if (!submissionContent.trim() || !selectedAssignment) return;
    submitMutation.mutate({
      assignmentId: selectedAssignment.id,
      data: { content: submissionContent },
    });
  };

  const getSubmissionForAssignment = (assignmentId) => {
    return mySubmissions.find((s) => s.assignment_id === assignmentId);
  };

  if (assignmentsLoading || submissionsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading assignments...</div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'graded':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'submitted':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Assignments</h2>

      {/* Submit Form */}
      {showSubmitForm && selectedAssignment && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Submit Assignment: {selectedAssignment.title}
          </h3>
          <div className="space-y-4">
            <textarea
              placeholder="Enter your submission content..."
              value={submissionContent}
              onChange={(e) => setSubmissionContent(e.target.value)}
              rows={8}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setShowSubmitForm(false);
                  setSubmissionContent('');
                  setSelectedAssignment(null);
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitMutation.isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <Send size={20} />
                {submitMutation.isLoading ? 'Submitting...' : 'Submit'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assignments List */}
      <div className="grid gap-4">
        {assignments.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <p className="text-lg">No assignments available</p>
            <p className="text-sm">Check back later for new assignments</p>
          </div>
        ) : (
          assignments.map((assignment) => {
            const submission = getSubmissionForAssignment(assignment.id);
            return (
              <div
                key={assignment.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      {assignment.title}
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                      {assignment.description || 'No description provided'}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                      {assignment.due_date && (
                        <span className="flex items-center gap-1">
                          <Clock size={16} />
                          Due: {new Date(assignment.due_date).toLocaleDateString()}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <FileText size={16} />
                        Max Score: {assignment.max_score}
                      </span>
                    </div>
                    {submission && (
                      <div className="mb-3">
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${getStatusColor(submission.status)}`}>
                          {submission.status === 'graded' && <CheckCircle size={16} />}
                          {submission.status === 'submitted' && <Clock size={16} />}
                          {submission.status.charAt(0).toUpperCase() + submission.status.slice(1)}
                        </span>
                        {submission.score !== null && (
                          <span className="ml-2 text-gray-600 dark:text-gray-400">
                            Score: {submission.score}/{assignment.max_score}
                          </span>
                        )}
                        {submission.feedback && (
                          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 p-2 rounded">
                            <strong>Feedback:</strong> {submission.feedback}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                  {!submission && (
                    <button
                      onClick={() => {
                        setSelectedAssignment(assignment);
                        setShowSubmitForm(true);
                      }}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Send size={20} />
                      Submit
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* My Submissions Section */}
      {mySubmissions.length > 0 && (
        <div className="mt-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">My Submissions</h3>
          <div className="grid gap-4">
            {mySubmissions.map((submission) => (
              <div
                key={submission.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${getStatusColor(submission.status)}`}>
                        {submission.status === 'graded' && <CheckCircle size={16} />}
                        {submission.status === 'submitted' && <Clock size={16} />}
                        {submission.status.charAt(0).toUpperCase() + submission.status.slice(1)}
                      </span>
                      {submission.score !== null && (
                        <span className="text-gray-600 dark:text-gray-400">
                          Score: {submission.score}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 mb-2">
                      {submission.content || 'No content provided'}
                    </p>
                    {submission.feedback && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 p-2 rounded">
                        <strong>Feedback:</strong> {submission.feedback}
                      </p>
                    )}
                  </div>
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Submitted: {submission.submitted_at ? new Date(submission.submitted_at).toLocaleDateString() : 'N/A'}
                  {submission.graded_at && ` • Graded: ${new Date(submission.graded_at).toLocaleDateString()}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentAssignments;
