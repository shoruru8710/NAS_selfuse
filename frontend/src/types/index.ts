export interface User {
  id: number;
  username: string;
  email: string;
  avatar_url: string;
  private_quota: number;
  paid_quota: number;
}

export interface Folder {
  id: string;
  name: string;
  parent: string | null;
  created_at: string;
  updated_at: string;
}

export interface File {
  id: string;
  name: string;
  folder: string | null;
  size_bytes: number;
  mime_type: string;
  visibility: 'private' | 'limited' | 'paid' | 'public';
  public_priority: number;
  cover_thumb: string | null;
  spine_thumb: string | null;
  spine_title: string;
  spine_color: string;
  last_access_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
