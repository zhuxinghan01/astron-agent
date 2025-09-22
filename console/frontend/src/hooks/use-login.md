实现一个登录注册逻辑，有以下几个接口，代码写在use-login.ts中，不涉及页面，只实现逻辑

/api/auth/validate 验证
request
{
"token": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9..."
}
response
{
"code": 1073741824,
"message": "string",
"data": {
"valid": true,
"tokenType": "access",
"uid": 1,
"username": "testuser",
"nickname": "测试用户",
"avatar": "https://example.com/avatar.jpg",
"issuedAt": "2025-09-09T09:20:26.811Z",
"expiresAt": "2025-09-09T09:20:26.811Z",
"revoked": false,
"revokeReason": "用户主动登出"
},
"timestamp": 9007199254740991
}

/api/auth/register
用户注册
request
{
"username": "alice",
"password": "P@ssw0rd",
"nickname": "Alice",
"avatar": "https://example.com/avatar.png"
}
response
{
"code": 1073741824,
"message": "string",
"data": {
"accessToken": "eyJhbGciOiJIUzUxMiJ9...",
"refreshToken": "eyJhbGciOiJIUzUxMiJ9...",
"accessTokenIssuedAt": "2024-01-01T12:00:00",
"accessTokenExpiresAt": "2024-01-01T13:00:00",
"refreshTokenIssuedAt": "2024-01-01T12:00:00",
"refreshTokenExpiresAt": "2024-01-08T12:00:00",
"tokenType": "Bearer"
},
"timestamp": 9007199254740991
}

/api/auth/refresh
刷新令牌
request
{
"refreshToken": "eyJhbGciOiJIUzUxMiJ9..."
}

response
{
"code": 1073741824,
"message": "string",
"data": {
"accessToken": "eyJhbGciOiJIUzUxMiJ9...",
"refreshToken": "eyJhbGciOiJIUzUxMiJ9...",
"accessTokenIssuedAt": "2024-01-01T12:00:00",
"accessTokenExpiresAt": "2024-01-01T13:00:00",
"refreshTokenIssuedAt": "2024-01-01T12:00:00",
"refreshTokenExpiresAt": "2024-01-08T12:00:00",
"tokenType": "Bearer"
},
"timestamp": 9007199254740991
}

/api/auth/logout
用户登出
request
{
"accessToken": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9...",
"refreshToken": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9..."
}
response code 200
{
"code": 1073741824,
"message": "string",
"data": {},
"timestamp": 9007199254740991
}

/api/auth/login
用户登录
request
{
"username": "alice",
"password": "P@ssw0rd"
}

response code 200
{
"code": 1073741824,
"message": "string",
"data": {
"accessToken": "eyJhbGciOiJIUzUxMiJ9...",
"refreshToken": "eyJhbGciOiJIUzUxMiJ9...",
"accessTokenIssuedAt": "2024-01-01T12:00:00",
"accessTokenExpiresAt": "2024-01-01T13:00:00",
"refreshTokenIssuedAt": "2024-01-01T12:00:00",
"refreshTokenExpiresAt": "2024-01-08T12:00:00",
"tokenType": "Bearer"
},
"timestamp": 9007199254740991
}
