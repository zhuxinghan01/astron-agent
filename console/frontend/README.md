## Casdoor 接入说明

### 1. 环境变量配置（.env 示例）

在前端根目录创建 `.env.local`（或 `.env.development` / `.env.production`）并填入以下内容：

```
VITE_BACKEND_SERVER_URL=https://your-backend.example.com

VITE_CASDOOR_SERVER_URL=https://door.example.com
VITE_CASDOOR_CLIENT_ID=your_client_id
VITE_CASDOOR_APP_NAME=your_app_name
VITE_CASDOOR_ORG_NAME=your_org_name
```

说明：

- `VITE_BACKEND_SERVER_URL`：前端回调组件会请求 `${VITE_BACKEND_SERVER_URL}/api/signin` 交换 `code`/`state` 为 token，请确保后端已实现该接口并返回 `accessToken`（可选 `refreshToken`）。
- `VITE_CASDOOR_*`：在 Casdoor 控制台创建应用后可获得。
- 回调地址请在 Casdoor 应用中配置为：`{前端域名}/callback`。

### 2. 前端集成点

- SDK 初始化：`src/config/index.ts`。
- 回调页面：`src/pages/callback/index.tsx`（PKCE：`exchangeForAccessToken` 直接从 Casdoor 换取 token）。
- 路由注册：`src/router/index.tsx` 中的 `/callback`。
- 静默登录：`src/pages/home-page/index.tsx` 使用 `SilentSignin`（当 URL 带 `silentSignin=1`）。
- 登录入口：登录弹窗 `src/components/login-modal/login-form-container.tsx` 中的“使用 Casdoor 登录”。

### 3. 登录模式

- 后端参与（默认示例）：使用 `AuthCallback` 调用 `${VITE_BACKEND_SERVER_URL}/api/signin` 交换 token。
- 前端直连（PKCE，本项目采用）：
  - 发起：`casdoorSdk.signin_redirect()`
  - 回调：`casdoorSdk.exchangeForAccessToken()`，拿到 `{ access_token, refresh_token }` 并写入 `localStorage`

### 4. 常用 API

- 登录跳转：`window.location.href = casdoorSdk.getSigninUrl()`
- 注册跳转：`window.location.href = casdoorSdk.getSignupUrl(true)`
- 用户资料页：`casdoorSdk.getMyProfileUrl()` / `casdoorSdk.getUserProfileUrl(userName)`

### 5. Token 存储

拦截器 `src/utils/http.ts` 会自动把 `Authorization: Bearer ${accessToken}` 注入请求头。PKCE 模式下，`/callback` 页面在完成 `exchangeForAccessToken` 后会将 `access_token` 写入 `localStorage.accessToken`。

# xingchen-pro-webapp
