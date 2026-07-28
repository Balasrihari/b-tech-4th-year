import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsService } from '../services/documents';
import { coursesService } from '../services/courses';
import { Upload, FileText, Trash2, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

const DocumentUpload = ({ userRole }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [formData, setFormData] = useState({
    title: '',
    document_type: 'study_material',
    description: '',
    course_id: '',
  });

  const queryClient = useQueryClient();

  // Fetch courses for dropdown
  const { data: courses = [] } = useQuery({
    queryKey: ['courses'],
    queryFn: () => coursesService.getAll(),
    enabled: userRole === 'faculty',
  });

  // Fetch documents
  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsService.getAll(),
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: documentsService.upload,
    onSuccess: () => {
      queryClient.invalidateQueries(['documents']);
      setSelectedFile(null);
      setFormData({
        title: '',
        document_type: 'study_material',
        description: '',
        course_id: '',
      });
      setUploadProgress(0);
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: documentsService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['documents']);
    },
  });

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      if (!formData.title) {
        setFormData({ ...formData, title: file.name.split('.')[0] });
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !formData.title) return;

    const uploadFormData = new FormData();
    uploadFormData.append('file', selectedFile);
    uploadFormData.append('title', formData.title);
    uploadFormData.append('document_type', formData.document_type);
    if (formData.description) {
      uploadFormData.append('description', formData.description);
    }
    if (formData.course_id) {
      uploadFormData.append('course_id', formData.course_id);
    }

    uploadMutation.mutate(uploadFormData);
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading documents...</div>
      </div>
    );
  }

  const getDocumentTypeColor = (type) => {
    switch (type) {
      case 'study_material':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'assignment':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'reference':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Documents</h2>
      </div>

      {/* Upload Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Upload Document</h3>
        <div className="space-y-4">
          {/* File Input */}
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
            <input
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.docx,.pptx,.xlsx,.txt,.md"
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
              <Upload size={48} className="text-gray-400 mb-2" />
              <p className="text-gray-600 dark:text-gray-400">
                {selectedFile ? selectedFile.name : 'Click to select a file'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                Supported: PDF, DOCX, PPTX, XLSX, TXT, MD
              </p>
            </label>
          </div>

          {/* Form Fields */}
          <input
            type="text"
            placeholder="Document title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />

          <textarea
            placeholder="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />

          <select
            value={formData.document_type}
            onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            <option value="study_material">Study Material</option>
            <option value="assignment">Assignment</option>
            <option value="reference">Reference</option>
            <option value="notes">Notes</option>
          </select>

          {userRole === 'faculty' && courses.length > 0 && (
            <select
              value={formData.course_id}
              onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">Select Course (optional)</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.code} - {course.title}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={handleUpload}
            disabled={!selectedFile || !formData.title || uploadMutation.isLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploadMutation.isLoading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload size={20} />
                Upload Document
              </>
            )}
          </button>
        </div>
      </div>

      {/* Documents List */}
      <div className="grid gap-4">
        {documents.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <p className="text-lg">No documents uploaded yet</p>
            <p className="text-sm">Upload your first document to get started</p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <FileText size={24} className="text-blue-600 dark:text-blue-400" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {doc.title}
                    </h3>
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${getDocumentTypeColor(doc.document_type)}`}>
                      {doc.document_type.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  {doc.description && (
                    <p className="text-gray-700 dark:text-gray-300 mb-2">
                      {doc.description}
                    </p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>Size: {formatFileSize(doc.file_size)}</span>
                    {doc.word_count && <span>Words: {doc.word_count}</span>}
                    {doc.page_count && <span>Pages: {doc.page_count}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    {doc.processing_status === 'completed' ? (
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs dark:bg-green-900 dark:text-green-200">
                        <CheckCircle size={12} />
                        Processed
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs dark:bg-yellow-900 dark:text-yellow-200">
                        <AlertCircle size={12} />
                        Processing
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors dark:text-gray-400 dark:hover:text-red-400 dark:hover:bg-red-900/20"
                >
                  <Trash2 size={20} />
                </button>
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Uploaded: {new Date(doc.created_at).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
