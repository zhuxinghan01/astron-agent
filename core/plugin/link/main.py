"""
Spark Link Server Main Entry Point

This module serves as the main entry point for the Spark Link server application.
It initializes the necessary environment variables for Polaris configuration
and starts the SparkLinkServer instance.
"""
import os
import subprocess
import sys
from pathlib import Path


def setup_python_path() -> None:
    """Set up Python path to include project root, parent directory, and grandparent directory"""
    # 获取当前脚本的路径和项目根目录
    current_file_path = Path(__file__)
    project_root = current_file_path.parent  # 项目根目录（当前目录）
    parent_dir = project_root.parent        # 上层目录
    grandparent_dir = parent_dir.parent      # 上上层目录

    # 获取当前的 PYTHONPATH
    python_path = os.environ.get("PYTHONPATH", "")

    # 检查并添加需要的目录
    new_paths = []
    for directory in [project_root, parent_dir, grandparent_dir]:
        if str(directory) not in python_path:
            new_paths.append(str(directory))

    # 如果有需要添加的路径，则更新 PYTHONPATH
    if new_paths:
        new_paths_str = os.pathsep.join(new_paths)
        if python_path:
            os.environ["PYTHONPATH"] = f"{new_paths_str}{os.pathsep}{python_path}"
        else:
            os.environ["PYTHONPATH"] = new_paths_str
        print(f"🔧 PYTHONPATH: {os.environ['PYTHONPATH']}")


def load_env_file(env_file: str) -> None:
    """Load environment variables from .env file"""
    if not os.path.exists(env_file):
        print(f"❌ Configuration file {env_file} does not exist")
        return

    print(f"📋 Loading configuration file: {env_file}")

    os.environ["CONFIG_ENV_PATH"] = (env_file)
    with open(env_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Parse environment variables
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
                print(f"  ✅ {key.strip()}={value.strip()}")
            else:
                print(f"  ⚠️  Line {line_num} format error: {line}")

    use_polaris = os.getenv("use_polaris", "false")
    if use_polaris == "false":
        return

    print(f"🔧 Config: use_polaris :{use_polaris}")
    load_polaris()


def load_polaris() -> None:
    """
    Load remote configuration and override environment variables
    """
    from common.settings.polaris import ConfigFilter, Polaris

    base_url = os.getenv("polaris_url")
    project_name = os.getenv("project_name", "hy-spark-agent-builder")
    cluster_group = os.getenv("polaris_cluster")
    service_name = os.getenv("service_name", "spark-link")
    version = os.getenv("version", "1.0.0")
    config_file = os.getenv("config_file", "config.env")
    config_filter = ConfigFilter(
        project_name=project_name,
        cluster_group=cluster_group,
        service_name=service_name,
        version=version,
        config_file=config_file,
    )
    username = os.getenv("polaris_username")
    password = os.getenv("polaris_password")

    # Ensure required parameters are not None
    if not base_url or not username or not password or not cluster_group:
        return  # Skip polaris config if required params are missing

    polaris = Polaris(base_url=base_url, username=username, password=password)
    try:
        _ = polaris.pull(
            config_filter=config_filter,
            retry_count=3,
            retry_interval=5,
            set_env=True,
        )
    except (ConnectionError, TimeoutError, ValueError) as e:
        print(
            f"⚠️ Polaris configuration loading failed, "
            f"continuing with local configuration: {e}"
        )


def start_service() -> None:
    """Start FastAPI service"""
    print("\n🚀 Starting Link service...")

    # Display key environment variables
    env_vars = [
        "PYTHONUNBUFFERED",
        "polaris_cluster",
        "polaris_url",
        "polaris_username",
        "run_environ",
        "use_polaris",
    ]

    print("📋 Environment configuration:")
    for var in env_vars:
        value = os.environ.get(var, "None")
        # Hide passwords
        if "password" in var.lower():
            value = "***"
        print(f"  - {var}: {value}")

    print("")

    try:
        # Start FastAPI application
        relative_path = (Path(__file__).resolve().parent).relative_to(Path.cwd()) / "app/start_server.py"
        if not relative_path.exists():
            raise FileNotFoundError(f"can not find {relative_path}")
        subprocess.run([sys.executable, relative_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Service startup failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Service stopped")
        sys.exit(0)


def main() -> None:
    """Main function"""
    print("🌟 Link Development Environment Launcher")
    print("=" * 50)

    # Set up Python path
    setup_python_path()

    # Load environment configuration
    config_file = Path(__file__).parent / "config.env"
    load_env_file(str(config_file))

    # Start service
    start_service()


if __name__ == "__main__":
    main()
