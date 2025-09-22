# 🔌 API 使用示例

本文档提供了星辰 RPA 服务器的详细 API 使用示例。

## 📋 目录

- [基本用法](#基本用法)
- [Python 客户端示例](#python-客户端示例)
- [JavaScript 客户端示例](#javascript-客户端示例)
- [cURL 示例](#curl-示例)
- [错误处理](#错误处理)
- [高级用法](#高级用法)

## 🚀 基本用法

### API 端点

- **基础 URL**: `http://localhost:19999`
- **API 版本**: `v1`
- **主要端点**: `/rpa/v1/exec`

### 认证

所有 API 请求都需要在请求头中包含 Bearer Token：

```
Authorization: Bearer <your-token>
```

## 🐍 Python 客户端示例

### 基本异步客户端

```python
import asyncio
import httpx
import json

class RPAClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def execute_task(self, project_id: str, params: dict = None,
                          exec_position: str = "EXECUTOR", sid: str = None):
        """执行 RPA 任务"""
        url = f"{self.base_url}/rpa/v1/exec"

        payload = {
            "project_id": project_id,
            "exec_position": exec_position,
            "params": params or {},
            "sid": sid or ""
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", url,
                headers=self.headers,
                json=payload,
                timeout=600  # 10分钟超时
            ) as response:
                if response.status_code != 200:
                    raise Exception(f"Request failed: {response.status_code}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # 去掉 "data: " 前缀
                            yield data
                        except json.JSONDecodeError:
                            continue

# 使用示例
async def main():
    client = RPAClient("http://localhost:19999", "your-token-here")

    try:
        async for event in client.execute_task(
            project_id="test-project-123",
            params={
                "action": "automate_task",
                "target": "web_scraping",
                "config": {
                    "url": "https://example.com",
                    "timeout": 30
                }
            },
            sid="unique-session-id"
        ):
            print(f"收到事件: {event}")

            # 检查任务状态
            if event.get("code") == 0:  # 成功
                print("✅ 任务执行成功")
                print(f"结果: {event.get('data')}")
                break
            elif event.get("code") != 0:  # 错误
                print(f"❌ 任务执行失败: {event.get('message')}")
                break

    except Exception as e:
        print(f"请求失败: {e}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
```

### 同步客户端版本

```python
import requests
import json
import time

class SyncRPAClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def execute_task(self, project_id: str, params: dict = None,
                    exec_position: str = "EXECUTOR", sid: str = None):
        """执行 RPA 任务 (同步版本)"""
        url = f"{self.base_url}/rpa/v1/exec"

        payload = {
            "project_id": project_id,
            "exec_position": exec_position,
            "params": params or {},
            "sid": sid or ""
        }

        with requests.post(
            url,
            headers=self.headers,
            json=payload,
            stream=True,
            timeout=600
        ) as response:
            if response.status_code != 200:
                raise Exception(f"Request failed: {response.status_code}")

            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        yield data
                    except json.JSONDecodeError:
                        continue

# 使用示例
def main():
    client = SyncRPAClient("http://localhost:19999", "your-token-here")

    for event in client.execute_task(
        project_id="test-project-123",
        params={"action": "test"},
        sid="sync-session-id"
    ):
        print(f"事件: {event}")

        if event.get("code") == 0:
            print("任务完成")
            break
        elif event.get("code") != 0:
            print("任务失败")
            break

if __name__ == "__main__":
    main()
```

## 🌐 JavaScript 客户端示例

### 使用 EventSource (浏览器)

```javascript
class RPAClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = token;
    }

    async executeTask(projectId, params = {}, execPosition = 'EXECUTOR', sid = '') {
        const url = `${this.baseUrl}/rpa/v1/exec`;

        const payload = {
            project_id: projectId,
            exec_position: execPosition,
            params: params,
            sid: sid
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            return {
                async *[Symbol.asyncIterator]() {
                    try {
                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;

                            const chunk = decoder.decode(value, { stream: true });
                            const lines = chunk.split('\n');

                            for (const line of lines) {
                                if (line.startsWith('data: ')) {
                                    try {
                                        const data = JSON.parse(line.substring(6));
                                        yield data;
                                    } catch (e) {
                                        console.warn('Failed to parse SSE data:', line);
                                    }
                                }
                            }
                        }
                    } finally {
                        reader.releaseLock();
                    }
                }
            };
        } catch (error) {
            throw new Error(`Request failed: ${error.message}`);
        }
    }
}

// 使用示例
async function main() {
    const client = new RPAClient('http://localhost:19999', 'your-token-here');

    try {
        const stream = await client.executeTask(
            'test-project-123',
            {
                action: 'web_automation',
                target: 'https://example.com'
            },
            'EXECUTOR',
            'js-session-id'
        );

        for await (const event of stream) {
            console.log('收到事件:', event);

            if (event.code === 0) {
                console.log('✅ 任务执行成功');
                console.log('结果:', event.data);
                break;
            } else if (event.code !== 0) {
                console.log('❌ 任务执行失败:', event.message);
                break;
            }
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}

// 运行示例
main();
```

### Node.js 客户端

```javascript
const https = require('https');
const http = require('http');

class NodeRPAClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = token;
    }

    executeTask(projectId, params = {}, execPosition = 'EXECUTOR', sid = '') {
        return new Promise((resolve, reject) => {
            const url = new URL(`${this.baseUrl}/rpa/v1/exec`);
            const payload = JSON.stringify({
                project_id: projectId,
                exec_position: execPosition,
                params: params,
                sid: sid
            });

            const options = {
                hostname: url.hostname,
                port: url.port,
                path: url.pathname,
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(payload)
                }
            };

            const client = url.protocol === 'https:' ? https : http;
            const req = client.request(options, (res) => {
                if (res.statusCode !== 200) {
                    reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
                    return;
                }

                const events = [];
                let buffer = '';

                res.on('data', (chunk) => {
                    buffer += chunk.toString();
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // 保留不完整的行

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                events.push(data);
                            } catch (e) {
                                console.warn('Failed to parse SSE data:', line);
                            }
                        }
                    }
                });

                res.on('end', () => {
                    resolve(events);
                });
            });

            req.on('error', reject);
            req.write(payload);
            req.end();
        });
    }
}

// 使用示例
async function main() {
    const client = new NodeRPAClient('http://localhost:19999', 'your-token-here');

    try {
        const events = await client.executeTask(
            'test-project-123',
            { action: 'node_automation' },
            'EXECUTOR',
            'node-session-id'
        );

        for (const event of events) {
            console.log('事件:', event);

            if (event.code === 0) {
                console.log('任务成功完成');
                break;
            } else if (event.code !== 0) {
                console.log('任务执行失败');
                break;
            }
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}

main();
```

## 🔧 cURL 示例

### 基本请求

```bash
curl -X POST "http://localhost:19999/rpa/v1/exec" \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-project-123",
    "exec_position": "EXECUTOR",
    "params": {
      "action": "test_automation",
      "target": "web"
    },
    "sid": "curl-session-id"
  }'
```

### 带超时的请求

```bash
curl -X POST "http://localhost:19999/rpa/v1/exec" \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -m 600 \
  --no-buffer \
  -d '{
    "project_id": "long-running-task",
    "exec_position": "EXECUTOR",
    "params": {
      "action": "batch_process",
      "items": 1000
    },
    "sid": "long-session-id"
  }'
```

### 使用环境变量

```bash
# 设置环境变量
export RPA_SERVER_URL="http://localhost:19999"
export RPA_TOKEN="your-token-here"

# 使用环境变量的请求
curl -X POST "${RPA_SERVER_URL}/rpa/v1/exec" \
  -H "Authorization: Bearer ${RPA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "env-test-project",
    "params": {"env": "production"}
  }'
```

## ❌ 错误处理

### 常见错误码

| 错误码 | 说明 | 处理方式 |
|-------|------|---------|
| 0 | 成功 | 正常处理结果 |
| 55001 | 创建任务错误 | 检查请求参数和 RPA API 配置 |
| 55002 | 查询任务错误 | 检查任务 ID 和网络连接 |
| 55003 | 超时错误 | 增加超时时间或检查任务复杂度 |
| 55999 | 未知错误 | 查看详细错误信息和日志 |

### Python 错误处理示例

```python
import asyncio
import httpx
import json

async def robust_execute_task(client, project_id, max_retries=3):
    """带重试机制的任务执行"""
    for attempt in range(max_retries):
        try:
            async for event in client.execute_task(project_id):
                code = event.get("code")
                message = event.get("message", "")

                if code == 0:  # 成功
                    return event.get("data")
                elif code == 55003:  # 超时
                    print(f"任务超时，尝试重试 ({attempt + 1}/{max_retries})")
                    break
                elif code in [55001, 55002]:  # 任务创建/查询错误
                    print(f"任务执行错误: {message}")
                    if "Invalid project" in message:
                        raise ValueError(f"无效的项目ID: {project_id}")
                    break
                else:  # 其他错误
                    print(f"未知错误 (代码: {code}): {message}")
                    break
        except httpx.RequestError as e:
            print(f"网络请求错误: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
            else:
                raise
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            break

    raise Exception(f"任务执行失败，已重试 {max_retries} 次")

# 使用示例
async def main():
    client = RPAClient("http://localhost:19999", "your-token")

    try:
        result = await robust_execute_task(client, "test-project-123")
        print(f"任务成功完成: {result}")
    except Exception as e:
        print(f"最终失败: {e}")

asyncio.run(main())
```

## 🚀 高级用法

### 批量任务执行

```python
import asyncio
import aiohttp
import json

class BatchRPAClient:
    def __init__(self, base_url: str, token: str, max_concurrent: int = 5):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def execute_single_task(self, session, task_config):
        """执行单个任务"""
        async with self.semaphore:
            url = f"{self.base_url}/rpa/v1/exec"

            try:
                async with session.post(url, headers=self.headers, json=task_config) as response:
                    if response.status != 200:
                        return {
                            "task_id": task_config.get("sid"),
                            "status": "failed",
                            "error": f"HTTP {response.status}"
                        }

                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if data.get("code") == 0:
                                    return {
                                        "task_id": task_config.get("sid"),
                                        "status": "completed",
                                        "result": data.get("data")
                                    }
                                elif data.get("code") != 0:
                                    return {
                                        "task_id": task_config.get("sid"),
                                        "status": "failed",
                                        "error": data.get("message")
                                    }
                            except json.JSONDecodeError:
                                continue

            except Exception as e:
                return {
                    "task_id": task_config.get("sid"),
                    "status": "error",
                    "error": str(e)
                }

    async def execute_batch(self, task_configs):
        """批量执行任务"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.execute_single_task(session, config)
                for config in task_configs
            ]

            return await asyncio.gather(*tasks, return_exceptions=True)

# 使用示例
async def batch_example():
    client = BatchRPAClient("http://localhost:19999", "your-token", max_concurrent=3)

    # 定义批量任务
    tasks = [
        {
            "project_id": "project-1",
            "params": {"action": "task1"},
            "sid": "batch-task-1"
        },
        {
            "project_id": "project-2",
            "params": {"action": "task2"},
            "sid": "batch-task-2"
        },
        {
            "project_id": "project-3",
            "params": {"action": "task3"},
            "sid": "batch-task-3"
        }
    ]

    # 执行批量任务
    results = await client.execute_batch(tasks)

    # 处理结果
    for result in results:
        if isinstance(result, Exception):
            print(f"任务异常: {result}")
        else:
            print(f"任务 {result['task_id']}: {result['status']}")
            if result['status'] == 'completed':
                print(f"  结果: {result['result']}")
            elif result['status'] in ['failed', 'error']:
                print(f"  错误: {result['error']}")

asyncio.run(batch_example())
```

### 任务进度监控

```python
import asyncio
import time
from datetime import datetime

class ProgressMonitor:
    def __init__(self, client):
        self.client = client
        self.start_time = None
        self.last_update = None

    async def execute_with_progress(self, project_id, params=None, sid=None):
        """带进度监控的任务执行"""
        self.start_time = time.time()
        self.last_update = self.start_time

        print(f"🚀 开始执行任务: {project_id}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            async for event in self.client.execute_task(project_id, params, sid=sid):
                current_time = time.time()
                elapsed = current_time - self.start_time

                print(f"\n📊 任务状态更新 (耗时: {elapsed:.2f}s)")
                print(f"   代码: {event.get('code')}")
                print(f"   消息: {event.get('message')}")

                if event.get('data'):
                    print(f"   数据: {event.get('data')}")

                # 检查任务完成
                if event.get("code") == 0:
                    print(f"\n✅ 任务完成! 总耗时: {elapsed:.2f}s")
                    return event.get("data")
                elif event.get("code") != 0:
                    print(f"\n❌ 任务失败! 耗时: {elapsed:.2f}s")
                    raise Exception(f"任务失败: {event.get('message')}")

                self.last_update = current_time

        except Exception as e:
            elapsed = time.time() - self.start_time
            print(f"\n💥 任务异常! 耗时: {elapsed:.2f}s")
            print(f"   错误: {e}")
            raise

# 使用示例
async def monitor_example():
    client = RPAClient("http://localhost:19999", "your-token")
    monitor = ProgressMonitor(client)

    try:
        result = await monitor.execute_with_progress(
            project_id="complex-task",
            params={
                "action": "data_processing",
                "items_count": 1000,
                "batch_size": 50
            },
            sid="monitor-session"
        )
        print(f"🎉 最终结果: {result}")

    except Exception as e:
        print(f"💔 执行失败: {e}")

asyncio.run(monitor_example())
```

---

## 📞 需要帮助？

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-org/xingchen-rpa-server/issues)
- 📖 **详细文档**: [README.md](./README.md)
- 🧪 **测试指南**: [TEST_SUMMARY.md](./TEST_SUMMARY.md)

这些示例涵盖了常见的使用场景，您可以根据具体需求进行调整和扩展。