import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { aiFeaturesService } from '../services/aiFeatures';
import { Map, Calendar, Clock, Target, Loader2, ChevronRight, CheckCircle } from 'lucide-react';

const AIRoadmap = () => {
  const [formData, setFormData] = useState({
    subject: '',
    duration_weeks: 4,
    hours_per_week: 10,
  });
  const [roadmap, setRoadmap] = useState(null);

  const roadmapMutation = useMutation({
    mutationFn: (data) => aiFeaturesService.generateStudyPlan(data.subject, data.duration_weeks, data.hours_per_week),
    onSuccess: (data) => {
      setRoadmap(data.plan);
    },
  });

  const handleGenerate = (e) => {
    e.preventDefault();
    if (!formData.subject.trim()) return;

    setRoadmap(null);
    roadmapMutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-3 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
          <Map size={24} className="text-indigo-600 dark:text-indigo-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">AI Roadmap Generator</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">Generate personalized learning roadmaps with AI</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <form onSubmit={handleGenerate}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Subject / Topic
              </label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="e.g., Machine Learning, Calculus, Organic Chemistry"
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                disabled={roadmapMutation.isLoading}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} />
                    Duration (weeks)
                  </div>
                </label>
                <select
                  value={formData.duration_weeks}
                  onChange={(e) => setFormData({ ...formData, duration_weeks: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  disabled={roadmapMutation.isLoading}
                >
                  <option value={2}>2 weeks</option>
                  <option value={4}>4 weeks</option>
                  <option value={6}>6 weeks</option>
                  <option value={8}>8 weeks</option>
                  <option value={12}>12 weeks</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <div className="flex items-center gap-2">
                    <Clock size={16} />
                    Hours per week
                  </div>
                </label>
                <select
                  value={formData.hours_per_week}
                  onChange={(e) => setFormData({ ...formData, hours_per_week: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  disabled={roadmapMutation.isLoading}
                >
                  <option value={5}>5 hours</option>
                  <option value={10}>10 hours</option>
                  <option value={15}>15 hours</option>
                  <option value={20}>20 hours</option>
                  <option value={25}>25 hours</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={!formData.subject.trim() || roadmapMutation.isLoading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {roadmapMutation.isLoading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Generating Roadmap...
                </>
              ) : (
                <>
                  <Map size={20} />
                  Generate Roadmap
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Roadmap Display */}
      {roadmap && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-6">
            <Target size={20} className="text-indigo-600 dark:text-indigo-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Learning Roadmap for {formData.subject}
            </h3>
          </div>

          {/* Weekly Goals */}
          <div className="mb-6">
            <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Calendar size={16} />
              Weekly Goals
            </h4>
            <div className="space-y-2">
              {roadmap.weekly_goals?.map((goal, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
                    {idx + 1}
                  </div>
                  <span className="text-gray-700 dark:text-gray-300">{goal}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Daily Schedule */}
          <div className="mb-6">
            <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Clock size={16} />
              Daily Schedule
            </h4>
            <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
              <p className="text-gray-700 dark:text-gray-300">{roadmap.daily_schedule}</p>
            </div>
          </div>

          {/* Topics */}
          <div className="mb-6">
            <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Target size={16} />
              Topics to Cover
            </h4>
            <div className="flex flex-wrap gap-2">
              {roadmap.topics?.map((topic, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 rounded-full text-sm"
                >
                  <ChevronRight size={12} />
                  {topic}
                </span>
              ))}
            </div>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <CheckCircle size={16} />
              Recommended Resources
            </h4>
            <div className="space-y-2">
              {roadmap.resources?.map((resource, idx) => (
                <div key={idx} className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                  <CheckCircle size={16} className="text-green-600 dark:text-green-400" />
                  {resource}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIRoadmap;
