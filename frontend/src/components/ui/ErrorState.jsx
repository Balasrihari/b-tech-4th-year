import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

const ErrorState = ({ message = 'Something went wrong', onRetry, showRetry = true }) => {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex flex-col items-center gap-4 max-w-md text-center">
        <div className="p-4 bg-red-100 dark:bg-red-900/20 rounded-full">
          <AlertCircle size={48} className="text-red-600 dark:text-red-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Error
          </h3>
          <p className="text-gray-600 dark:text-gray-400">{message}</p>
        </div>
        {showRetry && onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw size={20} />
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorState;
