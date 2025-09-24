// Add RPA Modal 相关类型定义
import { ToolItem } from '@/types/resource';

// RPA列表项接口
export interface RpaListItem extends ToolItem {
  rpaId?: string;
  platform?: string;
  avatarColor?: string;
  address?: string;
  inputs?: Array<{
    id: string;
    name: string;
    type?: string;
    required?: boolean;
  }>;
  outputs?: Array<{
    id: string;
    name: string;
    type?: string;
  }>;
}

// 获取RPA列表的请求参数接口
export interface GetRpasParams {
  content?: string;
  status?: number;
  pageNo: number;
  pageSize: number;
}

// 获取RPA列表的响应接口
export interface GetRpasResponse {
  data: RpaListItem[];
  total?: number;
  [key: string]: unknown;
}

// RPA节点数据接口
export interface RpaNodeData {
  nodeParam?: {
    toolId?: string;
    operationId?: string;
    rpaId?: string;
    version?: string;
    description?: string;
    platform?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

// RPA节点接口
export interface RpaNode {
  id: string;
  nodeType?: string;
  data?: RpaNodeData;
  [key: string]: unknown;
}

// Modal 组件的 Props 接口
export interface AddRpaModalProps {
  // 可以为空，因为组件目前没有 props
}
