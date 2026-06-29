"""辩论AI辅助写作系统 — 启动入口（支持 Railway/Render/Zeabur 等云平台）

用法:
  python run.py                    # 开发模式
  python run.py --prod             # 生产模式
  python run.py --port 8080        # 自定义端口
"""

import os
import sys
import argparse

# 确保 backend 包可导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动辩论AI辅助写作系统")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int,
                        default=int(os.getenv("PORT", 8000)),
                        help="监听端口（默认读取 $PORT 环境变量，未设置则 8000）")
    parser.add_argument("--prod", action="store_true",
                        help="生产模式（关闭热重载）")
    args = parser.parse_args()

    import uvicorn

    print(f"辩论AI助手启动中 — {args.host}:{args.port}")
    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=not args.prod,
        workers=1 if not args.prod else 4,
        log_level="info"
    )
