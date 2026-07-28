import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { rolesService } from '../services/roles';
import { Plus, Edit, Trash2, Save, X, Shield, CheckCircle, XCircle } from 'lucide-react';

const RoleManager = ({ userRole }) => {
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [showInactive, setShowInactive] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permissions: '',
    is_active: true,
  });

  const queryClient = useQueryClient();

  // Fetch roles
  const { data: roles = [], isLoading } = useQuery({
    queryKey: ['roles', showInactive],
    queryFn: () => rolesService.getAll({ is_active: showInactive ? undefined : true }),
    enabled: userRole === 'admin',
  });

  // Create role mutation
  const createMutation = useMutation({
    mutationFn: rolesService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['roles']);
      setIsCreating(false);
      resetForm();
    },
  });

  // Update role mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => rolesService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['roles']);
      setEditingId(null);
      resetForm();
    },
  });

  // Delete role mutation
  const deleteMutation = useMutation({
    mutationFn: rolesService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['roles']);
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      permissions: '',
      is_active: true,
    });
  };

  const handleCreate = () => {
    if (!formData.name.trim()) return;
    createMutation.mutate(formData);
  };

  const handleUpdate = (id) => {
    if (!formData.name.trim()) return;
    updateMutation.mutate({ id, data: formData });
  };

  const handleEdit = (role) => {
    setFormData({
      name: role.name,
      description: role.description || '',
      permissions: role.permissions || '',
      is_active: role.is_active,
    });
    setEditingId(role.id);
  };

  const handleDelete = (id, name) => {
    if (name.toLowerCase() in ['student', 'faculty', 'admin']) {
      alert('Cannot delete system roles (student, faculty, admin)');
      return;
    }
    if (window.confirm('Are you sure you want to delete this role?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleToggleActive = (id, currentStatus) => {
    updateMutation.mutate({
      id,
      data: { is_active: !currentStatus },
    });
  };

  if (userRole !== 'admin') {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        <p className="text-lg">Role management is for administrators only</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading roles...</div>
      </div>
    );
  }

  const isSystemRole = (name) => ['student', 'faculty', 'admin'].includes(name.toLowerCase());

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Shield size={28} />
          Role Management
        </h2>
        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          New Role
        </button>
      </div>

      {/* Filter Toggle */}
      <div className="flex items-center gap-2">
        <label className="text-sm text-gray-600 dark:text-gray-400">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="mr-2"
          />
          Show inactive roles
        </label>
      </div>

      {/* Create Role Form */}
      {isCreating && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Create New Role</h3>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Role name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <textarea
              placeholder="Role description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <textarea
              placeholder="Permissions (JSON format)"
              value={formData.permissions}
              onChange={(e) => setFormData({ ...formData, permissions: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono text-sm"
            />
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="mr-2"
              />
              <label className="text-sm text-gray-600 dark:text-gray-400">Active</label>
            </div>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setIsCreating(false);
                  resetForm();
                }}
                className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500"
              >
                <X size={20} />
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={createMutation.isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <Save size={20} />
                {createMutation.isLoading ? 'Creating...' : 'Create Role'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Roles List */}
      <div className="grid gap-4">
        {roles.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <p className="text-lg">No roles found</p>
            <p className="text-sm">Create your first role to get started</p>
          </div>
        ) : (
          roles.map((role) => (
            <div
              key={role.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
            >
              {editingId === role.id ? (
                <div className="space-y-4">
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                  <textarea
                    value={formData.permissions}
                    onChange={(e) => setFormData({ ...formData, permissions: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono text-sm"
                  />
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      className="mr-2"
                    />
                    <label className="text-sm text-gray-600 dark:text-gray-400">Active</label>
                  </div>
                  <div className="flex gap-2 justify-end">
                    <button
                      onClick={() => {
                        setEditingId(null);
                        resetForm();
                      }}
                      className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500"
                    >
                      <X size={20} />
                      Cancel
                    </button>
                    <button
                      onClick={() => handleUpdate(role.id)}
                      disabled={updateMutation.isLoading}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                    >
                      <Save size={20} />
                      {updateMutation.isLoading ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                          {role.name}
                        </h3>
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${
                          role.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {role.is_active ? <CheckCircle size={16} /> : <XCircle size={16} />}
                          {role.is_active ? 'Active' : 'Inactive'}
                        </span>
                        {isSystemRole(role.name) && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm dark:bg-purple-900 dark:text-purple-200">
                            System
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700 dark:text-gray-300 mb-2">
                        {role.description || 'No description provided'}
                      </p>
                      {role.permissions && (
                        <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Permissions:</p>
                          <pre className="text-xs text-gray-700 dark:text-gray-300 overflow-x-auto">
                            {role.permissions}
                          </pre>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleToggleActive(role.id, role.is_active)}
                        className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors dark:text-gray-400 dark:hover:text-green-400 dark:hover:bg-green-900/20"
                        title={role.is_active ? 'Deactivate' : 'Activate'}
                      >
                        {role.is_active ? <XCircle size={20} /> : <CheckCircle size={20} />}
                      </button>
                      <button
                        onClick={() => handleEdit(role)}
                        className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors dark:text-gray-400 dark:hover:text-blue-400 dark:hover:bg-blue-900/20"
                      >
                        <Edit size={20} />
                      </button>
                      {!isSystemRole(role.name) && (
                        <button
                          onClick={() => handleDelete(role.id, role.name)}
                          className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors dark:text-gray-400 dark:hover:text-red-400 dark:hover:bg-red-900/20"
                        >
                          <Trash2 size={20} />
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Created: {new Date(role.created_at).toLocaleDateString()}
                    {role.updated_at && ` • Updated: ${new Date(role.updated_at).toLocaleDateString()}`}
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RoleManager;
