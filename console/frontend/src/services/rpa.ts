import { PageData, ToolItem } from "@/types/resource";
import http from "@/utils/http";

export async function listRpas(params: {
  content?: string;
  status?: number;
  pageNo: number;
  pageSize: number;
}): Promise<PageData<ToolItem>> {
  return await http.get(`/tool/list-tools`, { params, responseType: "json" });
}

export async function createRpa(params: {
  sdk: string;
  sd1k: string;
  sdk22: string;
}): Promise<unknown> {
  return await http.post(`/rpa/create`, params);
}
