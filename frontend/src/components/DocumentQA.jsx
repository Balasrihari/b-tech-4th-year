import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { aiFeaturesService } from '../services/aiFeatures';
import { ragService } from '../services/rag';
import { MessageSquare, FileText, BookOpen, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

const DocumentQA = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [sources, setSources] = useState([]);
  const [useRag, setUseRag] = useState(true);

  const qaMutation = useMutation({
    mutationFn: (data) => aiFeaturesService.answerQuestion(data.question, data.useRag),
    onSuccess: (data) => {
      setAnswer(data.answer);
    },
  });

  const ragMutation = useMutation({
    mutationFn: (query) => ragService.retrieve(query, 5, true, true, true),
    onSuccess: (data) => {
      setSources(data.results || []);
    },
  });

  const handleAsk = (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setAnswer(null);
    setSources([]);
    qaMutation.mutate({ question, useRag });

    if (useRag) {
      ragMutation.mutate(question);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
            <MessageSquare size={24} className="text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Document Q&A</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">Ask questions and get answers with source citations</p>
          </div>
        </div>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={useRag}
            onChange={(e) => setUseRag(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">Use Document Context</span>
        </label>
      </div>

      {/* Question Input */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <form onSubmit={handleAsk}>
          <div className="space-y-4">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your documents..."
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
              disabled={qaMutation.isLoading}
            />
            <button
              type="submit"
              disabled={!question.trim() || qaMutation.isLoading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {qaMutation.isLoading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <MessageSquare size={20} />
                  Ask Question
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Answer */}
      {answer && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle size={20} className="text-green-600 dark:text-green-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Answer</h3>
          </div>
          <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
            {answer.split('\n').map((paragraph, idx) => (
              <p key={idx} className="mb-3">{paragraph}</p>
            ))}
          </div>
        </div>
      )}

      {/* Sources */}
      {sources.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen size={20} className="text-blue-600 dark:text-blue-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Source Documents</h3>
          </div>
          <div className="space-y-3">
            {sources.map((source, idx) => (
              <div
                key={idx}
                className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
              >
                <div className="flex items-start gap-3">
                  <FileText size={16} className="text-gray-500 dark:text-gray-400 mt-1" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {source.document_id || `Source ${idx + 1}`}
                      </span>
                      {source.score && (
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          Relevance: {(source.score * 100).toFixed(1)}%
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
                      {source.text || source.content || 'No content available'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Sources Warning */}
      {useRag && ragMutation.isSuccess && sources.length === 0 && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center gap-2">
            <AlertCircle size={20} className="text-yellow-600 dark:text-yellow-400" />
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              No relevant documents found. Try uploading documents or disable "Use Document Context" for general AI answers.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentQA;
