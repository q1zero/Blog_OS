"""
GitHub回调URL设置辅助脚本

这个脚本帮助检测当前环境并更新settings.py中的GITHUB_CALLBACK_URLS配置
运行方式：python -m utils.github_auth.setup_callback
"""

import os
import re
import socket
import sys
from pathlib import Path


def get_replit_domain():
    """
    获取Replit环境中的域名，优先返回HTTPS版本
    """
    try:
        # 硬编码的Replit域名（优先HTTPS版本）
        replit_domain_base = "blog-os-235.replit.app"
        replit_domains = [
            f"https://{replit_domain_base}",  # HTTPS版本（优先）
            f"http://{replit_domain_base}",  # HTTP版本（备用）
        ]

        # 获取Replit环境变量作为备用方法
        if not replit_domains:
            repl_slug = os.environ.get("REPL_SLUG", "")
            repl_owner = os.environ.get("REPL_OWNER", "")

            if repl_slug and repl_owner:
                base_domain = f"{repl_slug}.{repl_owner}.repl.co"
                return [f"https://{base_domain}", f"http://{base_domain}"]

        return replit_domains
    except Exception as e:
        print(f"获取Replit域名错误: {e}")
        return []


def get_all_possible_domains():
    """
    获取所有可能的域名，包括本地开发和Replit
    """
    domains = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    # 获取本机IP地址
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        if ip_address and ip_address not in ("127.0.0.1", "localhost"):
            domains.append(f"http://{ip_address}:8000")
    except Exception as e:
        print(f"获取本机IP地址错误: {e}")

    # 获取Replit域名（HTTP和HTTPS两个版本）
    replit_domains = get_replit_domain()
    if replit_domains:
        domains.extend(replit_domains)

    return domains


def update_settings_file():
    """
    更新settings.py文件中的GITHUB_CALLBACK_URLS配置
    """
    # 获取settings.py文件路径
    try:
        # 获取当前文件的目录
        current_dir = Path(__file__).resolve().parent
        # 获取settings.py文件路径
        settings_path = current_dir.parent.parent / "config" / "settings.py"

        if not settings_path.exists():
            print(f"找不到settings.py文件: {settings_path}")
            return False

        # 读取settings.py文件内容
        with open(settings_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 获取所有可能的域名
        domains = get_all_possible_domains()
        callback_urls = [f"{domain}/accounts/github/callback" for domain in domains]

        # 检查是否已经存在GITHUB_CALLBACK_URLS配置
        if "GITHUB_CALLBACK_URLS" in content:
            # 使用正则表达式更新已存在的配置
            pattern = r"GITHUB_CALLBACK_URLS\s*=\s*\[(.*?)\]"
            replacement = (
                "GITHUB_CALLBACK_URLS = [\n    "
                + ",\n    ".join([f'"{url}"' for url in callback_urls])
                + "\n]"
            )
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # 如果不存在，在文件末尾添加配置
            github_config = "\n# GitHub OAuth配置\n# 配置所有可能的回调URL\n"
            github_config += (
                "GITHUB_CALLBACK_URLS = [\n    "
                + ",\n    ".join([f'"{url}"' for url in callback_urls])
                + "\n]\n\n"
            )
            github_config += "# 使用第一个URL作为默认回调URL\n"
            github_config += "GITHUB_CALLBACK_URL = GITHUB_CALLBACK_URLS[0]\n"

            # 在文件末尾添加配置
            new_content = content + github_config

        # 写入新的配置
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"已更新GitHub回调URL配置:\n{callback_urls}\n")
        print("注意: 您需要在GitHub OAuth应用设置中添加这些回调URL")
        return True

    except Exception as e:
        print(f"更新settings.py文件错误: {e}")
        return False


def main():
    """
    主函数
    """
    print("GitHub回调URL设置辅助工具")
    print("=" * 50)

    # 检测当前环境
    print("检测当前环境...")
    domains = get_all_possible_domains()
    print(f"检测到的域名: {domains}")

    # 提示用户更新设置
    while True:
        choice = input("是否更新settings.py文件中的GitHub回调URL配置? (y/n): ")
        if choice.lower() in ("y", "yes"):
            if update_settings_file():
                print("\n配置更新成功!")
                print("请确保在GitHub OAuth应用设置中添加所有这些回调URL")
                print(
                    "登录GitHub > Settings > Developer settings > OAuth Apps > 您的应用"
                )
                print(
                    "在「Authorization callback URL」字段中添加每个回调URL（每行一个）"
                )
            else:
                print("配置更新失败!")
            break
        elif choice.lower() in ("n", "no"):
            print("已取消更新配置")
            break
        else:
            print("无效的选择，请输入y或n")


if __name__ == "__main__":
    main()
