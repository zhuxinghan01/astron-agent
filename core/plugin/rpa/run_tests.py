#!/usr/bin/env python3
"""测试运行脚本。

这个脚本用于运行项目的各种测试套件。
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """运行命令并返回结果。"""
    print(f"\n{'='*50}")
    print(f"运行: {description}")
    print(f"命令: {command}")
    print("=" * 50)

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print("✅ 成功")
        if result.stdout:
            print("输出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失败")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False


def main() -> int:
    """主函数。"""
    print("🚀 开始运行 RPA 服务器测试套件")

    # 切换到项目目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    test_commands = [
        ("python -m pytest tests/api/test_schemas.py -v", "API Schemas 测试"),
        ("python -m pytest tests/errors/test_error_code.py -v", "错误码测试"),
        ("python -m pytest tests/exceptions/test_config_exceptions.py -v", "异常测试"),
        ("python -m pytest tests/consts/test_const.py -v", "常量测试"),
        ("python -m pytest tests/utils/test_utl_util.py -v", "工具函数测试"),
        ("python -m pytest tests/api/test_router.py -v", "路由测试"),
    ]

    passed = 0
    failed = 0

    for command, description in test_commands:
        if run_command(command, description):
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*50}")
    print("🎯 测试总结")
    print(f"{'='*50}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {passed + failed}")

    if failed == 0:
        print("\n🎉 所有测试都通过了！")
        return 0

    print(f"\n⚠️  有 {failed} 个测试套件失败")
    return 1


if __name__ == "__main__":
    import os

    sys.exit(main())
