import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingState = ({ message = 'Loading...', size = 'default' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    default: 'w-6 h-6',
    large: 'w-8 h-8',
  };

  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex flex-col items-center gap-3">
        <Loader2 size={size === 'large' ? 48 : size === 'small' ? 24 : 32} className={`text-blue-600 dark:text-blue-400 animate-spin ${sizeClasses[size]}`} />
        <p className="text-gray-500 dark:text-gray-400">{message}</p>
      </div>
    </div>
  );
};

export default LoadingState;
