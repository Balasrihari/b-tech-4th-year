import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersService } from '../services/users';
import { Edit2, Trash2, Shield, UserX, UserCheck } from 'lucide-react';

export default function UserManager() {
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const queryClient = useQueryClient();

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: usersService.getAll,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => usersService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      setEditingId(null);
      setEditData({});
    },
  });

  const deleteMutation = useMutation({
    mutationFn: usersService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });

  const handleEdit = (user) => {
    setEditingId(user.id);
    setEditData({ full_name: user.full_name, is_active: user.is_active });
  };

  const handleSaveEdit = (user) => {
    updateMutation.mutate({ id: user.id, data: editData });
  };

  const handleToggleActive = (user) => {
    updateMutation.mutate({ id: user.id, data: { is_active: !user.is_active } });
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>Loading users...</div>;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">User Management</h2>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Email</th>
              <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Name</th>
              <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Role</th>
              <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Status</th>
              <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users?.map((user) => (
              <tr key={user.id} className="border-b border-gray-200 dark:border-gray-700">
                <td className="py-3 px-4 text-gray-900 dark:text-white">{user.email}</td>
                <td className="py-3 px-4">
                  {editingId === user.id ? (
                    <input
                      type="text"
                      value={editData.full_name}
                      onChange={(e) => setEditData({ ...editData, full_name: e.target.value })}
                      className="px-2 py-1 border rounded dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <span className="text-gray-900 dark:text-white">{user.full_name}</span>
                  )}
                </td>
                <td className="py-3 px-4">
                  <span className="flex items-center gap-2">
                    <Shield size={16} className="text-gray-600 dark:text-gray-400" />
                    <span className="text-gray-900 dark:text-white capitalize">{user.role}</span>
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span
                    className={`px-2 py-1 rounded-full text-xs ${
                      user.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}
                  >
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex gap-2">
                    {editingId === user.id ? (
                      <>
                        <button
                          onClick={() => handleSaveEdit(user)}
                          className="px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => handleEdit(user)}
                          className="p-1 text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
                        >
                          <Edit2 size={16} />
                        </button>
                        <button
                          onClick={() => handleToggleActive(user)}
                          className="p-1 text-gray-600 dark:text-gray-300 hover:text-green-600 dark:hover:text-green-400"
                          title={user.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {user.is_active ? <UserX size={16} /> : <UserCheck size={16} />}
                        </button>
                        <button
                          onClick={() => handleDelete(user.id)}
                          className="p-1 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400"
                        >
                          <Trash2 size={16} />
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
