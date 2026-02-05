import React, { useState, useRef, useCallback } from 'react';
import { api } from '../api/client';
import { Upload, X, File as FileIcon, CheckCircle, AlertCircle } from 'lucide-react';

interface UploadModalProps {
  folderId: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

const UploadModal: React.FC<UploadModalProps> = ({ folderId, onClose, onSuccess }) => {
  const [files, setFiles] = useState<UploadingFile[]>([]);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback((fileList: FileList) => {
    const newFiles: UploadingFile[] = Array.from(fileList).map((file) => ({
      file,
      progress: 0,
      status: 'pending' as const,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);

    for (let i = 0; i < files.length; i++) {
      const uploadingFile = files[i];
      if (uploadingFile.status !== 'pending') continue;

      setFiles((prev) =>
        prev.map((f, idx) =>
          idx === i ? { ...f, status: 'uploading' as const, progress: 10 } : f
        )
      );

      try {
        // Step 1: Initialize upload
        const initResponse = await api.initUpload(
          uploadingFile.file.name,
          uploadingFile.file.type || 'application/octet-stream',
          uploadingFile.file.size,
          folderId || undefined
        );

        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, progress: 30 } : f
          )
        );

        const sessionId = initResponse.data.session_id;

        // Step 2: Upload file
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, progress: 50 } : f
          )
        );

        await api.uploadChunk(sessionId, uploadingFile.file, folderId || undefined);

        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: 'success' as const, progress: 100 } : f
          )
        );
      } catch (error: any) {
        console.error('Upload failed:', error);
        const errorMsg = error.response?.data?.detail || 'アップロードに失敗しました';
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: 'error' as const, error: errorMsg } : f
          )
        );
      }
    }

    setUploading(false);

    // Check if all files uploaded successfully
    const allSuccess = files.every((f) => f.status === 'success');
    if (allSuccess) {
      setTimeout(onSuccess, 500);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const hasSuccessFiles = files.some((f) => f.status === 'success');
  const hasPendingFiles = files.some((f) => f.status === 'pending');

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>ファイルをアップロード</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        <div className="modal-body">
          <div
            className={`upload-area ${dragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={48} />
            <p>ファイルをドラッグ＆ドロップ</p>
            <span>または、クリックしてファイルを選択</span>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              style={{ display: 'none' }}
              onChange={handleFileSelect}
            />
          </div>

          {files.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ marginBottom: '0.75rem', fontSize: '0.9rem', color: '#666' }}>
                アップロードファイル ({files.length})
              </h4>
              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {files.map((uploadingFile, index) => (
                  <div
                    key={index}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '0.75rem',
                      background: '#f9f9f9',
                      borderRadius: '8px',
                      marginBottom: '0.5rem',
                    }}
                  >
                    <FileIcon size={20} style={{ marginRight: '0.75rem', color: '#667eea' }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div
                        style={{
                          fontSize: '0.875rem',
                          fontWeight: 500,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {uploadingFile.file.name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#999' }}>
                        {formatFileSize(uploadingFile.file.size)}
                      </div>
                      {uploadingFile.status === 'uploading' && (
                        <div className="progress-bar" style={{ marginTop: '0.5rem' }}>
                          <div
                            className="progress-bar-fill"
                            style={{ width: `${uploadingFile.progress}%` }}
                          />
                        </div>
                      )}
                      {uploadingFile.status === 'error' && (
                        <div style={{ fontSize: '0.75rem', color: '#ef4444', marginTop: '0.25rem' }}>
                          {uploadingFile.error}
                        </div>
                      )}
                    </div>
                    {uploadingFile.status === 'pending' && (
                      <button
                        onClick={() => removeFile(index)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#999' }}
                      >
                        <X size={18} />
                      </button>
                    )}
                    {uploadingFile.status === 'success' && (
                      <CheckCircle size={20} style={{ color: '#22c55e' }} />
                    )}
                    {uploadingFile.status === 'error' && (
                      <AlertCircle size={20} style={{ color: '#ef4444' }} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            キャンセル
          </button>
          {hasSuccessFiles && !hasPendingFiles ? (
            <button className="btn btn-primary" onClick={onSuccess}>
              完了
            </button>
          ) : (
            <button
              className="btn btn-primary"
              onClick={uploadFiles}
              disabled={files.length === 0 || uploading || !hasPendingFiles}
            >
              {uploading ? 'アップロード中...' : 'アップロード'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
