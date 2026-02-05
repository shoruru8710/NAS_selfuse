import React from 'react';
import { api } from '../api/client';
import { File as FileType } from '../types';
import { X, Download, Trash2, Image, FileText, Film, Archive, File as FileIcon } from 'lucide-react';

interface FileDetailModalProps {
  file: FileType;
  onClose: () => void;
  onDelete: () => void;
  onUpdate: () => void;
}

const FileDetailModal: React.FC<FileDetailModalProps> = ({ file, onClose, onDelete, onUpdate }) => {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ja-JP');
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) return <Image size={48} />;
    if (mimeType.startsWith('video/')) return <Film size={48} />;
    if (mimeType.includes('pdf') || mimeType.includes('text')) return <FileText size={48} />;
    if (mimeType.includes('zip') || mimeType.includes('archive')) return <Archive size={48} />;
    return <FileIcon size={48} />;
  };

  const getVisibilityLabel = (visibility: string) => {
    const labels: { [key: string]: string } = {
      private: 'プライベート',
      limited: '限定公開',
      paid: '有料',
      public: '公開',
    };
    return labels[visibility] || visibility;
  };

  const handleDownload = () => {
    window.open(api.getDownloadUrl(file.id), '_blank');
  };

  const handleDelete = () => {
    if (window.confirm('このファイルを削除しますか？')) {
      onDelete();
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
        <div className="modal-header">
          <h2>ファイル詳細</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        <div className="modal-body">
          <div className="file-details">
            <div className="file-details-header">
              <div className="file-details-preview">
                {file.cover_thumb ? (
                  <img
                    src={file.cover_thumb}
                    alt={file.name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '12px' }}
                  />
                ) : (
                  getFileIcon(file.mime_type)
                )}
              </div>
              <div className="file-details-info">
                <h3>{file.name}</h3>
                <div className="file-details-meta">
                  <p><strong>サイズ:</strong> {formatFileSize(file.size_bytes)}</p>
                  <p><strong>タイプ:</strong> {file.mime_type}</p>
                  <p><strong>公開設定:</strong> {getVisibilityLabel(file.visibility)}</p>
                  <p><strong>作成日:</strong> {formatDate(file.created_at)}</p>
                  <p><strong>更新日:</strong> {formatDate(file.updated_at)}</p>
                </div>
              </div>
            </div>
            <div className="file-details-actions">
              <button className="btn btn-primary" onClick={handleDownload}>
                <Download size={16} />
                ダウンロード
              </button>
              <button className="btn btn-danger" onClick={handleDelete}>
                <Trash2 size={16} />
                削除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileDetailModal;
