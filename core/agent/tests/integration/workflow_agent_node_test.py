"""
工作流代理节点性能测试

这个测试脚本用于测试工作流代理节点的并发性能，通过多线程并发发送请求
来评估系统在高负载下的表现和响应时间。

主要功能：
- 并发测试OpenAI API调用
- 测量首帧响应时间
- 支持20个并发请求的压力测试
"""

import asyncio
import concurrent.futures
import time
from typing import Any, Dict, List

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionUserMessageParam

first_frame_times: List[str] = []

# 注意: 以下是一个备用的HTTP请求实现（已注释）
# 如需使用aiohttp版本，请取消注释并添加aiohttp依赖


async def do_request(url: str, request_data: Dict[str, Any], i: int) -> None:
    # 忽略未使用的参数，这是测试函数的占位符
    del url, request_data, i
    # TODO: 将API密钥移至环境变量或配置文件中
    client = AsyncOpenAI(
        api_key="sk-test-key-replace-with-env-var",
        base_url="https://maas-api.cn-huabei-1.xf-yun.com/v1",
    )
    messages: List[ChatCompletionUserMessageParam] = [
        ChatCompletionUserMessageParam(
            role="user",
            content=(
                "我想要在上海火车站到东方明珠之间找一个酒店，"
                "酒店应该在这两者之间的任意一个地铁站附近2公里范围内，"
                "价格在500到750之间，你能帮我找到所有符合条件的酒店吗？"
            ),
        )
    ]
    start_time = time.time()
    response = await client.chat.completions.create(
        model="xdeepseekv3",
        messages=messages,
        stream=True,
    )
    first = True
    async for chunk in response:
        if first:
            end_time = time.time()
            print(chunk)
            print(end_time - start_time)
            first = False


def task(url: str, request_data: Dict[str, Any], i: int) -> None:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(do_request(url, request_data, i))
    loop.close()


if __name__ == "__main__":
    # 创建一个线程池，最大工作线程数为 20
    # URL = "https://maas-api.cn-huabei-1.xf-yun.com/v1/chat/completions"
    URL = "http://127.0.0.1:17870/agent/v1/custom/chat/completions"
    data = {
        "model_config": {
            "domain": "xdeepseekv3",
            "api": "https://maas-api.cn-huabei-1.xf-yun.com/v1",
        },
        "instruction": {"reasoning": "优先使用工具", "answer": ""},
        "plugin": {
            "tools": [],
            "mcp_server_ids": [],
            "mcp_server_urls": [],
            "workflow_ids": [],
        },
        "uid": "",
        "messages": [
            {
                "role": "user",
                "content": (
                    "我想要在上海火车站到东方明珠之间找一个酒店，"
                    "酒店应该在这两者之间的任意一个地铁站附近2公里范围内，"
                    "价格在500到750之间，你能帮我找到所有符合条件的酒店吗？"
                ),
            }
        ],
        "meta_data": {
            "caller": "workflow-agent-node",
            "caller_sid": "spf0011029a@hf19615f729015741782",
        },
        "stream": True,
        "max_loop_count": 10,
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # 提交 20 个任务到线程池
        future_to_task = {executor.submit(task, URL, data, i + 1): i for i in range(20)}
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(future_to_task):
            task_id = future_to_task[future]
            try:
                future.result()
                print(f"Task {task_id + 1} completed successfully.")
            except (RuntimeError, OSError, ValueError) as exc:
                print(f"Task {task_id + 1} failed with exception: {exc}")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"Task {task_id + 1} failed with unexpected exception: {exc}")
