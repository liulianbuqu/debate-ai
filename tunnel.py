"""手机访问隧道 — 一键生成公网地址

用法:
  python tunnel.py                    # 启动隧道（使用已有 Docker 或直接启动）
  python tunnel.py --token xxx        # 首次使用：配置 ngrok token

首次使用:
  1. 打开 https://dashboard.ngrok.com/signup 免费注册
  2. 在 Dashboard → Your Authtoken 复制 token
  3. 运行: python tunnel.py --token 你的token

手机访问:
  - 生成 https://xxxx.ngrok-free.app 公网地址
  - 同一 WiFi 下也可用局域网地址
"""

import os
import sys
import time
import subprocess
import json as json_module
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NGROK_CONFIG_DIR = os.path.join(BASE_DIR, ".ngrok_config")


def ensure_server():
    """确保服务器在运行，优先用 Docker"""
    # 检查 Docker 是否已在运行
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=debate-ai", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    if "debate-ai" in result.stdout:
        print("✓ Docker 容器已运行")
        return "docker"

    # 检查端口是否已被占用（可能是其他方式启动的）
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    if result == 0:
        print("✓ 端口 8000 已有服务运行")
        return "existing"

    # 启动 Docker 容器
    print("正在启动 Docker 容器...")
    r = subprocess.run(["docker", "compose", "up", "-d"], cwd=BASE_DIR,
                       capture_output=True, text=True)
    if r.returncode == 0:
        time.sleep(3)
        print("✓ Docker 容器已启动")
        return "docker"

    # 如果 Docker 不可用，直接启动 Python 服务
    print("⚠ Docker 不可用，直接启动 Python 服务...")
    import threading, uvicorn
    sys.path.insert(0, BASE_DIR)
    from backend.main import app
    t = threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning"), daemon=True)
    t.start()
    time.sleep(2)
    print("✓ Python 服务已启动")
    return "python"


def main():
    parser = argparse.ArgumentParser(description="手机访问隧道")
    parser.add_argument("--token", help="ngrok authtoken（首次需要）")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # 配置 ngrok token
    if args.token:
        os.makedirs(NGROK_CONFIG_DIR, exist_ok=True)
        cfg = os.path.join(NGROK_CONFIG_DIR, "ngrok.yml")
        with open(cfg, "w") as f:
            f.write(f"version: '2'\nauthtoken: {args.token}\n")
        print("✓ ngrok token 已保存")

    # 确保服务在运行
    ensure_server()

    # 启动 ngrok 隧道
    from pyngrok import ngrok, conf
    conf.get_default().config_path = os.path.join(NGROK_CONFIG_DIR, "ngrok.yml")

    print("正在创建公网隧道...")
    try:
        tunnel = ngrok.connect(args.port, bind_tls=True)
        public_url = tunnel.public_url
    except Exception as e:
        print(f"\n⚠ ngrok 隧道创建失败: {e}")
        print("\n如果未配置 token，请运行:")
        print(f"  python tunnel.py --token 你的ngrok_token")
        print("\n获取免费 token: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("\n⚠ 临时方案 — 局域网地址（同一 WiFi 下可用）:")
        print(f"  http://10.133.138.215:{args.port}")
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n已退出")
        return

    # 打印访问地址
    print("\n" + "=" * 55)
    print("  📱 手机访问方式")
    print("=" * 55)
    print(f"\n  🌐 公网地址（随时随地，手机推荐）:")
    print(f"  \033[1;36m{public_url}\033[0m")
    print(f"\n  📶 局域网地址（同一 WiFi）:")
    print(f"  http://10.133.138.215:{args.port}")
    print("\n" + "-" * 55)
    print("  本窗口保持打开，按 Ctrl+C 停止")
    print("-" * 55)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止隧道...")
        ngrok.kill()
        print("隧道已关闭，再见！")


if __name__ == "__main__":
    main()
