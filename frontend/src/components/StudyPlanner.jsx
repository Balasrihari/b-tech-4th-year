import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studyPlansService } from '../services/studyPlans';
import { Plus, Calendar, Target, CheckCircle, Clock } from 'lucide-react';

export default function StudyPlanner() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ topic: '', target_date: '', priority: 'medium', estimated_hours: 1 });
  const queryClient = useQueryClient();

  const { data: plans, isLoading } = useQuery({
    queryKey: ['studyPlans'],
    queryFn: () => studyPlansService.getAll(false),
  });

  const { data: roadmap } = useQuery({
    queryKey: ['studyRoadmap'],
    queryFn: studyPlansService.getRoadmap,
  });

  const createMutation = useMutation({
    mutationFn: studyPlansService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['studyPlans']);
      queryClient.invalidateQueries(['studyRoadmap']);
      setShowForm(false);
      setFormData({ topic: '', target_date: '', priority: 'medium', estimated_hours: 1 });
    },
  });

  const toggleCompleteMutation = useMutation({
    mutationFn: ({ id, data }) => studyPlansService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['studyPlans']);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: studyPlansService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['studyPlans']);
    },
  });

  const handleCreate = (e) => {
    e.preventDefault();
    if (formData.topic.trim()) {
      createMutation.mutate({
        ...formData,
        target_date: formData.target_date ? new Date(formData.target_date).toISOString() : null
      });
    }
  };

  const handleToggleComplete = (plan) => {
    toggleCompleteMutation.mutate({
      id: plan.id,
      data: { is_completed: !plan.is_completed }
    });
  };

  if (isLoading) return <div>Loading study plans...</div>;

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Calendar size={24} />
            Study Planner
          </h2>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus size={20} />
            Add Plan
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleCreate} className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">New Study Plan</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Topic</label>
                <input
                  type="text"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Target Date</label>
                <input
                  type="date"
                  value={formData.target_date}
                  onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Estimated Hours</label>
                <input
                  type="number"
                  value={formData.estimated_hours}
                  onChange={(e) => setFormData({ ...formData, estimated_hours: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  min="1"
                />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button
                type="submit"
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        <div className="space-y-3">
          {plans?.length === 0 ? (
            <p className="text-gray-600 dark:text-gray-400 text-center py-8">No study plans yet. Add your first plan!</p>
          ) : (
            plans?.map((plan) => (
              <div
                key={plan.id}
                className={`p-4 border rounded-lg ${
                  plan.is_completed
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                    : 'bg-gray-50 dark:bg-gray-700/50 border-gray-200 dark:border-gray-600'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <button
                      onClick={() => handleToggleComplete(plan)}
                      className={`mt-1 p-2 rounded-full ${
                        plan.is_completed
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                      }`}
                    >
                      <CheckCircle size={16} />
                    </button>
                    <div>
                      <h4 className={`font-semibold ${plan.is_completed ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}`}>
                        {plan.topic}
                      </h4>
                      <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {plan.target_date && (
                          <span className="flex items-center gap-1">
                            <Clock size={14} />
                            {new Date(plan.target_date).toLocaleDateString()}
                          </span>
                        )}
                        <span className={`px-2 py-1 rounded ${
                          plan.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                          plan.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                          'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                        }`}>
                          {plan.priority}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteMutation.mutate(plan.id)}
                    className="p-1 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {roadmap && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Target size={20} />
            Study Roadmap
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Not Started</h4>
              <div className="space-y-1">
                {roadmap.not_started?.map((item, index) => (
                  <div key={index} className="text-sm p-2 bg-gray-100 dark:bg-gray-700 rounded">
                    {item.topic}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">In Progress</h4>
              <div className="space-y-1">
                {roadmap.in_progress?.map((item, index) => (
                  <div key={index} className="text-sm p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded">
                    {item.topic} ({item.mastery_level}%)
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Mastered</h4>
              <div className="space-y-1">
                {roadmap.mastered?.map((item, index) => (
                  <div key={index} className="text-sm p-2 bg-green-100 dark:bg-green-900/30 rounded">
                    {item.topic} ({item.mastery_level}%)
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
