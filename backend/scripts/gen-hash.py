#!/usr/bin/env python3
"""
生成管理员密码的 bcrypt 哈希

使用方法:
    python scripts/gen-hash.py

输入密码后，会生成适合 ADMIN_PASSWORD_HASH 环境变量的哈希值
"""

import getpass
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import hash_password


def main():
    print("=== 管理员密码哈希生成器 ===\n")

    # 从命令行参数或交互式输入获取密码
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = getpass.getpass("请输入管理员密码: ")
        confirm = getpass.getpass("确认密码: ")
        if password != confirm:
            print("错误: 两次输入的密码不匹配", file=sys.stderr)
            sys.exit(1)

    if not password:
        print("错误: 密码不能为空", file=sys.stderr)
        sys.exit(1)

    # 生成哈希
    password_hash = hash_password(password)

    print(f"\n生成的 bcrypt 哈希值:\n{password_hash}\n")
    print("请将此值设置到环境变量 ADMIN_PASSWORD_HASH 中")
    print("例如在 .env 文件中添加:")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")


if __name__ == "__main__":
    main()
