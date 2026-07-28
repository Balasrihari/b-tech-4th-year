import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { todosService } from '../services/todos';
import { Plus, Check, Trash2, Edit2 } from 'lucide-react';

export default function TodoList() {
  const [newTodo, setNewTodo] = useState({ title: '', description: '', priority: 'medium' });
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const queryClient = useQueryClient();

  const { data: todos, isLoading } = useQuery({
    queryKey: ['todos'],
    queryFn: todosService.getAll,
  });

  const createMutation = useMutation({
    mutationFn: todosService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['todos']);
      setNewTodo({ title: '', description: '', priority: 'medium' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => todosService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['todos']);
      setEditingId(null);
      setEditData({});
    },
  });

  const deleteMutation = useMutation({
    mutationFn: todosService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['todos']);
    },
  });

  const handleCreate = (e) => {
    e.preventDefault();
    if (newTodo.title.trim()) {
      createMutation.mutate(newTodo);
    }
  };

  const handleToggleComplete = (todo) => {
    const newStatus = todo.status === 'completed' ? 'pending' : 'completed';
    updateMutation.mutate({ id: todo.id, data: { status: newStatus } });
  };

  const handleEdit = (todo) => {
    setEditingId(todo.id);
    setEditData({ title: todo.title, description: todo.description, priority: todo.priority });
  };

  const handleSaveEdit = (todo) => {
    updateMutation.mutate({ id: todo.id, data: editData });
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this todo?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>Loading todos...</div>;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Task Management</h2>
      
      <form onSubmit={handleCreate} className="mb-6">
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={newTodo.title}
            onChange={(e) => setNewTodo({ ...newTodo, title: e.target.value })}
            placeholder="Add a new task..."
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          />
          <select
            value={newTodo.priority}
            onChange={(e) => setNewTodo({ ...newTodo, priority: e.target.value })}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus size={20} />
            Add
          </button>
        </div>
        <textarea
          value={newTodo.description}
          onChange={(e) => setNewTodo({ ...newTodo, description: e.target.value })}
          placeholder="Description (optional)"
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          rows="2"
        />
      </form>

      <div className="space-y-3">
        {todos?.map((todo) => (
          <div
            key={todo.id}
            className={`p-4 border rounded-lg ${
              todo.status === 'completed'
                ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                : 'bg-gray-50 dark:bg-gray-700/50 border-gray-200 dark:border-gray-600'
            }`}
          >
            {editingId === todo.id ? (
              <div className="space-y-2">
                <input
                  type="text"
                  value={editData.title}
                  onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                  className="w-full px-3 py-2 border rounded dark:bg-gray-700 dark:text-white"
                />
                <textarea
                  value={editData.description}
                  onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded dark:bg-gray-700 dark:text-white"
                  rows="2"
                />
                <select
                  value={editData.priority}
                  onChange={(e) => setEditData({ ...editData, priority: e.target.value })}
                  className="px-3 py-2 border rounded dark:bg-gray-700 dark:text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSaveEdit(todo)}
                    className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-start gap-3">
                <button
                  onClick={() => handleToggleComplete(todo)}
                  className={`mt-1 p-2 rounded-full ${
                    todo.status === 'completed'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                  }`}
                >
                  <Check size={16} />
                </button>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3
                      className={`font-semibold ${
                        todo.status === 'completed'
                          ? 'line-through text-gray-500'
                          : 'text-gray-900 dark:text-white'
                      }`}
                    >
                      {todo.title}
                    </h3>
                    <span
                      className={`px-2 py-1 text-xs rounded ${
                        todo.priority === 'high'
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : todo.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      }`}
                    >
                      {todo.priority}
                    </span>
                  </div>
                  {todo.description && (
                    <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">{todo.description}</p>
                  )}
                  {todo.due_date && (
                    <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">
                      Due: {new Date(todo.due_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(todo)}
                    className="p-2 text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    <Edit2 size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(todo.id)}
                    className="p-2 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
