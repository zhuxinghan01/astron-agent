// 类型定义
export interface KnowledgeDetailProps {
  setCurrentTab: (tab: string) => void;
  parentId: number;
  setParentId: (id: number) => void;
  setFileId: (id: number) => void;
}

export interface EditChunkProps {
  setEditModal: (show: boolean) => void;
  currentChunk: ChunkItem;
  enableChunk: (chunk: ChunkItem, checked: boolean) => void;
  fileInfo: FileInfo;
}

export interface FileDetailProps {
  setCurrentTab: (tab: string) => void;
  fileId: number;
  setFileId: (id: number) => void;
}

export interface KnowledgeFileItem {
  id: number;
  name: string;
  type: string;
  isFile: boolean;
  fileId?: number;
  fileInfoV2?: {
    charCount: number;
    enabled: boolean;
    size: number;
  };
  hitCount: number;
  createTime: string;
  auditSuggest?: string;
}

export interface ChunkItem {
  id: number;
  content: string;
  markdownContent: string;
  enabled: boolean;
  charCount: number;
  testHitCount: number;
  index: number;
  tagDtoList: TagItem[];
  auditSuggest?: string;
  auditDetail?: string;
  source?: number;
}

export interface TagItem {
  type: number;
  tagName: string;
}

export interface FileInfo {
  name: string;
  type: string;
}

export interface DirectoryItem {
  name: string;
  parentId: number;
}

export interface PaginationState {
  current: number;
  pageSize: number;
  total: number;
}

export interface KnowledgeDetailModalInfo {
  open: boolean;
  nodeId: string;
  repoId: string;
  tag?: string;
}
