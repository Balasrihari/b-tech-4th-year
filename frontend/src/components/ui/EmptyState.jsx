import React from 'react';
import { Inbox, Plus, FileText, Users, BookOpen } from 'lucide-react';

const EmptyState = ({ 
  title = 'No data found', 
  description = 'There are no items to display at this time.',
  icon = 'inbox',
  action = null,
  actionLabel = 'Add New'
}) => {
  const icons = {
    inbox: Inbox,
    plus: Plus,
    file: FileText,
    users: Users,
    book: BookOpen,
  };

  const Icon = icons[icon] || Inbox;

  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex flex-col items-center gap-4 max-w-md text-center">
        <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-full">
          <Icon size={48} className="text-gray-400 dark:text-gray-500" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            {title}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">{description}</p>
        </div>
        {action && (
          <button
            onClick={action}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            {actionLabel}
          </button>
        )}
      </div>
    </div>
  );
};

export default EmptyState;
