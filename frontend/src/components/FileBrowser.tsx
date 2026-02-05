import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import { Folder, File as FileType, PaginatedResponse } from '../types';
import {
  Folder as FolderIcon,
  File as FileIcon,
  Upload,
  FolderPlus,
  Download,
  Trash2,
  ChevronRight,
  Home,
  Image,
  FileText,
  Film,
  Archive,
  RefreshCw,
} from 'lucide-react';
import UploadModal from './UploadModal';
import CreateFolderModal from './CreateFolderModal';
import FileDetailModal from './FileDetailModal';

const FileBrowser: React.FC = () => {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [files, setFiles] = useState<FileType[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string | null>(null);
  const [folderPath, setFolderPath] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<{ type: 'file' | 'folder'; item: FileType | Folder } | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showCreateFolderModal, setShowCreateFolderModal] = useState(false);
  const [showFileDetailModal, setShowFileDetailModal] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [foldersRes, filesRes] = await Promise.all([
        api.getFolders(currentFolder || undefined),
        api.getMyFiles(currentFolder || undefined),
      ]);
      setFolders((foldersRes.data as PaginatedResponse<Folder>).results);
      setFiles((filesRes.data as PaginatedResponse<FileType>).results);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  }, [currentFolder]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const navigateToFolder = async (folderId: string | null) => {
    if (folderId === null) {
      setCurrentFolder(null);
      setFolderPath([]);
    } else {
      setCurrentFolder(folderId);
      // Build folder path
      try {
        const folder = folders.find((f) => f.id === folderId);
        if (folder) {
          setFolderPath((prev) => [...prev, folder]);
        }
      } catch (error) {
        console.error('Failed to navigate:', error);
      }
    }
    setSelectedItem(null);
  };

  const navigateToBreadcrumb = (index: number) => {
    if (index === -1) {
      setCurrentFolder(null);
      setFolderPath([]);
    } else {
      const folder = folderPath[index];
      setCurrentFolder(folder.id);
      setFolderPath(folderPath.slice(0, index + 1));
    }
    setSelectedItem(null);
  };

  const handleFolderClick = (folder: Folder) => {
    navigateToFolder(folder.id);
  };

  const handleFileClick = (file: FileType) => {
    setSelectedItem({ type: 'file', item: file });
    setShowFileDetailModal(true);
  };

  const handleDelete = async () => {
    if (!selectedItem) return;

    const confirmMsg = selectedItem.type === 'folder'
      ? 'このフォルダを削除しますか？'
      : 'このファイルを削除しますか？';

    if (!window.confirm(confirmMsg)) return;

    try {
      if (selectedItem.type === 'folder') {
        await api.deleteFolder(selectedItem.item.id);
      } else {
        await api.deleteFile(selectedItem.item.id);
      }
      setSelectedItem(null);
      fetchData();
    } catch (error) {
      console.error('Failed to delete:', error);
      alert('削除に失敗しました');
    }
  };

  const handleDownload = () => {
    if (selectedItem?.type === 'file') {
      window.open(api.getDownloadUrl(selectedItem.item.id), '_blank');
    }
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) return <Image size={32} />;
    if (mimeType.startsWith('video/')) return <Film size={32} />;
    if (mimeType.includes('pdf') || mimeType.includes('text')) return <FileText size={32} />;
    if (mimeType.includes('zip') || mimeType.includes('archive')) return <Archive size={32} />;
    return <FileIcon size={32} />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="file-browser">
      <div className="toolbar">
        <div className="toolbar-left">
          <div className="breadcrumb">
            <span
              className={`breadcrumb-item ${currentFolder === null ? 'active' : ''}`}
              onClick={() => navigateToBreadcrumb(-1)}
            >
              <Home size={16} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
              Home
            </span>
            {folderPath.map((folder, index) => (
              <React.Fragment key={folder.id}>
                <ChevronRight size={14} className="breadcrumb-separator" />
                <span
                  className={`breadcrumb-item ${index === folderPath.length - 1 ? 'active' : ''}`}
                  onClick={() => navigateToBreadcrumb(index)}
                >
                  {folder.name}
                </span>
              </React.Fragment>
            ))}
          </div>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-outline" onClick={fetchData}>
            <RefreshCw size={16} />
          </button>
          <button className="btn btn-secondary" onClick={() => setShowCreateFolderModal(true)}>
            <FolderPlus size={16} />
            New Folder
          </button>
          <button className="btn btn-primary" onClick={() => setShowUploadModal(true)}>
            <Upload size={16} />
            Upload
          </button>
          {selectedItem?.type === 'file' && (
            <button className="btn btn-secondary" onClick={handleDownload}>
              <Download size={16} />
            </button>
          )}
          {selectedItem && (
            <button className="btn btn-danger" onClick={handleDelete}>
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      <div className="file-list">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : folders.length === 0 && files.length === 0 ? (
          <div className="file-list-empty">
            <FolderIcon size={64} />
            <p>このフォルダは空です</p>
            <p style={{ fontSize: '0.875rem' }}>
              ファイルをアップロードするか、新しいフォルダを作成してください
            </p>
          </div>
        ) : (
          <div className="item-grid">
            {folders.map((folder) => (
              <div
                key={folder.id}
                className={`item-card ${selectedItem?.item.id === folder.id ? 'selected' : ''}`}
                onClick={() => handleFolderClick(folder)}
              >
                <div className="item-icon folder">
                  <FolderIcon size={32} />
                </div>
                <div className="item-name">{folder.name}</div>
              </div>
            ))}
            {files.map((file) => (
              <div
                key={file.id}
                className={`item-card ${selectedItem?.item.id === file.id ? 'selected' : ''}`}
                onClick={() => handleFileClick(file)}
              >
                <div className="item-icon">
                  {file.cover_thumb ? (
                    <img src={file.cover_thumb} alt={file.name} />
                  ) : (
                    getFileIcon(file.mime_type)
                  )}
                </div>
                <div className="item-name">{file.name}</div>
                <div className="item-meta">{formatFileSize(file.size_bytes)}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showUploadModal && (
        <UploadModal
          folderId={currentFolder}
          onClose={() => setShowUploadModal(false)}
          onSuccess={() => {
            setShowUploadModal(false);
            fetchData();
          }}
        />
      )}

      {showCreateFolderModal && (
        <CreateFolderModal
          parentId={currentFolder}
          onClose={() => setShowCreateFolderModal(false)}
          onSuccess={() => {
            setShowCreateFolderModal(false);
            fetchData();
          }}
        />
      )}

      {showFileDetailModal && selectedItem?.type === 'file' && (
        <FileDetailModal
          file={selectedItem.item as FileType}
          onClose={() => {
            setShowFileDetailModal(false);
            setSelectedItem(null);
          }}
          onDelete={() => {
            setShowFileDetailModal(false);
            handleDelete();
          }}
          onUpdate={fetchData}
        />
      )}
    </div>
  );
};

export default FileBrowser;
