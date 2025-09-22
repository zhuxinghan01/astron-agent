"""
Complete API Test Suite

Run tests for all API interfaces and generate unified test reports:
1. Chat Completions API
2. Custom Chat Completions API
3. Bot Config Management API

Use fixed test parameters to ensure consistency and reproducibility.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, Tuple


class APITestRunner:
    """API测试运行器"""

    def __init__(self) -> None:
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()

    def run_test_file(self, test_file: str, test_name: str) -> Dict[str, Any]:
        """运行单个测试文件并返回结果"""
        print(f"\n🚀 运行{test_name}测试...")
        print("=" * 60)

        start_time = time.time()

        try:
            # 运行测试文件
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                check=False,  # 不自动检查返回码
            )

            end_time = time.time()
            execution_time = end_time - start_time

            # 解析结果
            success = result.returncode == 0
            output = result.stdout
            errors = result.stderr

            # 从输出中提取统计信息
            passed, failed, total = self.parse_test_statistics(output)

            test_result = {
                "success": success,
                "execution_time": execution_time,
                "passed": passed,
                "failed": failed,
                "total": total,
                "output": output,
                "errors": errors,
            }

            print(f"✅ {test_name}测试完成 - 耗时: {execution_time:.2f}s")
            print(f"📊 结果: 通过 {passed}, 失败 {failed}, 总计 {total}")

            if not success:
                print("❌ 测试执行失败:")
                print(errors)

            return test_result

        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name}测试超时")
            return {
                "success": False,
                "execution_time": 300,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "output": "",
                "errors": "测试执行超时",
            }
        except (OSError, ValueError, RuntimeError) as e:
            print(f"❌ 运行{test_name}测试时发生异常: {e}")
            return {
                "success": False,
                "execution_time": 0,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "output": "",
                "errors": str(e),
            }

    def parse_test_statistics(self, output: str) -> Tuple[int, int, int]:
        """从测试输出中解析统计信息"""
        passed, failed, total = 0, 0, 0

        # 查找测试完成的统计信息
        lines = output.split("\n")
        for line in lines:
            if "测试完成！通过:" in line:
                try:
                    # 解析形如 "📊 测试完成！通过: 12, 失败: 0, 总计: 12" 的行
                    parts = line.split("通过: ")[1]
                    passed = int(parts.split(",")[0].strip())

                    failed_part = parts.split("失败: ")[1]
                    failed = int(failed_part.split(",")[0].strip())

                    total_part = parts.split("总计: ")[1]
                    total = int(total_part.strip())

                    break
                except (IndexError, ValueError):
                    continue

        return passed, failed, total

    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有API测试"""
        print("🧪 开始运行完整API测试套件...")
        print(f"⏰ 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # 定义要运行的测试
        tests = [
            ("tests/integration/test_chat_completions_v2.py", "Chat Completions"),
            (
                "tests/integration/test_custom_chat_completions.py",
                "Custom Chat Completions",
            ),
            (
                "tests/integration/test_bot_config_management.py",
                "Bot Config Management",
            ),
        ]

        # 运行每个测试
        for test_file, test_name in tests:
            self.test_results[test_name] = self.run_test_file(test_file, test_name)

        # 生成汇总报告
        return self.generate_summary_report()

    def generate_summary_report(self) -> Dict[str, Any]:
        """生成汇总测试报告"""
        end_time = datetime.now()
        total_execution_time = (end_time - self.start_time).total_seconds()

        # 计算总体统计
        total_passed = sum(result["passed"] for result in self.test_results.values())
        total_failed = sum(result["failed"] for result in self.test_results.values())
        total_tests = sum(result["total"] for result in self.test_results.values())

        successful_suites = sum(
            1 for result in self.test_results.values() if result["success"]
        )
        total_suites = len(self.test_results)

        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        summary = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_execution_time": total_execution_time,
            "total_suites": total_suites,
            "successful_suites": successful_suites,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": success_rate,
            "suite_results": self.test_results,
        }

        return summary

    def print_final_report(self, summary: Dict[str, Any]) -> None:
        """打印最终测试报告"""
        print("\n" + "=" * 80)
        print("🏁 API测试套件执行完成")
        print("=" * 80)

        print(f"⏰ 总执行时间: {summary['total_execution_time']:.2f}秒")
        print(
            f"📦 测试套件: {summary['successful_suites']}/"
            f"{summary['total_suites']} 成功"
        )
        print(f"🧪 测试用例: {summary['total_passed']}/{summary['total_tests']} 通过")
        print(f"📊 成功率: {summary['success_rate']:.1f}%")

        print("\n📋 详细结果:")
        for suite_name, result in summary["suite_results"].items():
            status = "✅" if result["success"] else "❌"
            print(
                f"  {status} {suite_name}: {result['passed']}/{result['total']} "
                f"通过 (耗时: {result['execution_time']:.1f}s)"
            )

        if summary["total_failed"] > 0:
            print(f"\n⚠️ 发现 {summary['total_failed']} 个失败的测试用例")
            print("详细错误信息请查看上方的测试输出。")
        else:
            print(f"\n🎉 所有 {summary['total_tests']} 个测试用例都通过了！")

        print("\n💡 测试配置信息:")
        print("  - x-consumer-username: cb7386a7")
        print("  - bot_id: 14a9bbbcf0254f9b94562e6705d3a13f")
        print("  - uid: 12")
        print("  - 服务地址: http://localhost:17870")

        print("=" * 80)

    def save_detailed_report(
        self, summary: Dict[str, Any], filename: str = "api_test_report.json"
    ) -> None:
        """保存详细的JSON格式测试报告"""
        report_path = f"tests/{filename}"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"📄 详细测试报告已保存至: {report_path}")


def main() -> None:
    """主函数"""
    runner = APITestRunner()

    try:
        # 运行所有测试
        summary = runner.run_all_tests()

        # 打印最终报告
        runner.print_final_report(summary)

        # 保存详细报告
        runner.save_detailed_report(summary)

        # 根据测试结果设置退出码
        if summary["total_failed"] == 0:
            print("\n🎊 所有API测试成功完成！")
            sys.exit(0)
        else:
            print(f"\n⚠️ 有 {summary['total_failed']} 个测试失败")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断了测试执行")
        sys.exit(130)
    except (RuntimeError, ValueError, OSError) as e:
        print(f"\n❌ 测试运行器发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
