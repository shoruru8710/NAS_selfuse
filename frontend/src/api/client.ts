import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://shorunas.com';

const client = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const api = {
  // Auth
  getMe: () => client.get('/api/accounts/me/'),
  logout: () => client.post('/api/accounts/logout/'),
  getLoginUrl: () => `${API_BASE_URL}/api/accounts/oauth/login/`,

  // Folders
  getFolders: (parentId?: string) =>
    client.get('/api/files/folders/', { params: { parent_id: parentId } }),
  createFolder: (name: string, parentId?: string) =>
    client.post('/api/files/folders/', { name, parent: parentId }),
  deleteFolder: (id: string) => client.delete(`/api/files/folders/${id}/`),

  // Files
  getMyFiles: (folderId?: string) =>
    client.get('/api/files/me/', { params: { folder_id: folderId } }),
  getPublicFiles: (folderId?: string) =>
    client.get('/api/files/public/', { params: { folder_id: folderId } }),
  getFile: (id: string) => client.get(`/api/files/${id}/`),
  updateFile: (id: string, data: any) => client.patch(`/api/files/${id}/`, data),
  deleteFile: (id: string) => client.delete(`/api/files/${id}/`),
  getDownloadUrl: (id: string) => `${API_BASE_URL}/api/files/${id}/download/`,

  // Upload
  initUpload: (filename: string, mimeType: string, sizeBytes: number, folderId?: string) =>
    client.post('/api/files/upload/init/', {
      filename,
      mime_type: mimeType,
      size_bytes: sizeBytes,
      folder_id: folderId,
    }),
  uploadChunk: (sessionId: string, file: File, folderId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (folderId) formData.append('folder_id', folderId);
    return client.post(`/api/files/upload/${sessionId}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getUploadStatus: (sessionId: string) =>
    client.get(`/api/files/upload/${sessionId}/status/`),

  // Thumbnails
  uploadThumbnail: (fileId: string, type: 'cover' | 'spine', file: File) => {
    const formData = new FormData();
    formData.append('type', type);
    formData.append('file', file);
    return client.post(`/api/files/${fileId}/thumbnail/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Sort Order
  updateSortOrder: (folderId: string, items: Array<{ item_type: string; item_id: string; sort_index: number }>) =>
    client.put(`/api/files/folders/${folderId}/sort/`, { items }),
};

export default client;
