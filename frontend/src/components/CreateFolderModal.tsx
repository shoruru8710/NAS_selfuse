import React, { useState } from 'react';
import { api } from '../api/client';
import { X } from 'lucide-react';

interface CreateFolderModalProps {
  parentId: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateFolderModal: React.FC<CreateFolderModalProps> = ({ parentId, onClose, onSuccess }) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('フォルダ名を入力してください');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.createFolder(name.trim(), parentId || undefined);
      onSuccess();
    } catch (error: any) {
      console.error('Failed to create folder:', error);
      setError(error.response?.data?.detail || 'フォルダの作成に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>新しいフォルダ</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label htmlFor="folder-name">フォルダ名</label>
              <input
                id="folder-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="フォルダ名を入力"
                autoFocus
              />
            </div>
            {error && (
              <div style={{ color: '#ef4444', fontSize: '0.875rem' }}>{error}</div>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              キャンセル
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '作成中...' : '作成'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateFolderModal;
