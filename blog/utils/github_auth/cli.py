"""
GitHub认证命令行工具
"""
import argparse
from .management import clean_social_apps, create_github_app, reset_github_app

def main():
    """
    命令行入口
    """
    parser = argparse.ArgumentParser(description='GitHub认证管理工具')
    parser.add_argument('--clean', action='store_true', help='清理所有社交账号相关的对象')
    parser.add_argument('--create', action='store_true', help='创建GitHub应用配置')
    parser.add_argument('--reset', action='store_true', help='重置GitHub应用配置')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_social_apps()
    elif args.create:
        create_github_app()
    elif args.reset:
        reset_github_app()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
