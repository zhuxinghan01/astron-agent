import http from '../utils/http';

// TypeScript interfaces for the new notification structure
export interface Notification {
  id: number;
  type: string;
  title: string;
  body: string;
  templateCode: string | null;
  payload: string;
  creatorUid: string;
  createdAt: string;
  expireAt: string | null;
  meta: any | null;
  isRead: boolean;
  readAt: string | null;
  receivedAt: string;
}

export interface NotificationResponse {
  notifications: Notification[];
  pageIndex: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  unreadCount: number;
  notificationsByType: Record<string, Notification[]>;
}

/**
 * 获取消息分类
 * @returns 消息类型
 */
export const getAllMessageType = (): Promise<any> => {
  return http.post(`/xingchen-api/messageCenter/allTypes`);
};

/**
 * 获取全部消息
 * @param params  消息分类
 * @returns
 */
// 返回结果示例
// {
//   "notifications": [
//       {
//           "id": 3,
//           "type": "SYSTEM",
//           "title": "Space Invitation Reminder",
//           "body": "<h3>Space Invitation Reminder</h3>[CuteFox827] invited you to join space \"团队空间3\", <a href=\"https://localhost:3000/sharepage?param=76bce05905f50ef0c6c7b7bcd4b2b0bb284b7e273760c654ae6bf98d7929\" target=\"_blank\" style=\"color: blue;\">Click to view</a>\n",
//           "templateCode": null,
//           "payload": "{\"outlink\": \"https://localhost:3000/sharepage?param=76bce05905f50ef0c6c7b7bcd4b2b0bb284b7e273760c654ae6bf98d7929\"}",
//           "creatorUid": "683e976b-144f-446c-ba87-7a537209bb6a",
//           "createdAt": "2025-09-29T13:54:09.415",
//           "expireAt": null,
//           "meta": null,
//           "isRead": false,
//           "readAt": null,
//           "receivedAt": "2025-09-29T13:54:09.416"
//       }
//   ],
//   "pageIndex": 1,
//   "pageSize": 100,
//   "totalCount": 1,
//   "totalPages": 1,
//   "unreadCount": 1,
//   "notificationsByType": {
//       "SYSTEM": [
//           {
//               "id": 3,
//               "type": "SYSTEM",
//               "title": "Space Invitation Reminder",
//               "body": "<h3>Space Invitation Reminder</h3>[CuteFox827] invited you to join space \"团队空间3\", <a href=\"https://localhost:3000/sharepage?param=76bce05905f50ef0c6c7b7bcd4b2b0bb284b7e273760c654ae6bf98d7929\" target=\"_blank\" style=\"color: blue;\">Click to view</a>\n",
//               "templateCode": null,
//               "payload": "{\"outlink\": \"https://localhost:3000/sharepage?param=76bce05905f50ef0c6c7b7bcd4b2b0bb284b7e273760c654ae6bf98d7929\"}",
//               "creatorUid": "683e976b-144f-446c-ba87-7a537209bb6a",
//               "createdAt": "2025-09-29T13:54:09.415",
//               "expireAt": null,
//               "meta": null,
//               "isRead": false,
//               "readAt": null,
//               "receivedAt": "2025-09-29T13:54:09.416"
//           }
//       ]
//   }
// }
export const getAllMessage = (params: {
  type: string;
  unreadOnly: boolean;
  pageIndex: number;
  pageSize: number;
  offset: number;
}): Promise<NotificationResponse> => {
  return http.get(`/notifications/list`, { params });
};

/**
 * 修改消息状态已读
 * @param params  消息id
 * @returns
 */
export const changeMessageStatus = (params: {
  notificationIds: number[];
  markAll: boolean;
}): Promise<any> => {
  return http.post(`/notifications/mark-read`, params);
};

/**
 * 标记全部已读
 * @param params  消息分类
 * @returns
 */
export const readAllMessage = (params: any): Promise<any> => {
  return http.post(`/xingchen-api/messageCenter/clearUnread`, params);
};

/**
 * 获取维度消息数量
 * @param params 消息分类
 * @returns
 */
export const messageCount = (params: any): Promise<any> => {
  return http.post(`/notifications/unread-count`, params);
};

export const deleteMessage = (params: any): Promise<any> => {
  return http.delete(`/notifications/${params.id}`);
};
