"""
GitHub认证管理工具
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib.sites.models import Site
from django.conf import settings

def clean_social_apps():
    """
    清理所有社交账号相关的对象
    """
    try:
        # 删除所有SocialToken对象
        token_count = SocialToken.objects.all().count()
        if token_count > 0:
            print(f"删除 {token_count} 个SocialToken对象")
            SocialToken.objects.all().delete()
        else:
            print("没有找到SocialToken对象")
        
        # 删除所有SocialAccount对象
        account_count = SocialAccount.objects.all().count()
        if account_count > 0:
            print(f"删除 {account_count} 个SocialAccount对象")
            SocialAccount.objects.all().delete()
        else:
            print("没有找到SocialAccount对象")
        
        # 删除所有SocialApp对象
        app_count = SocialApp.objects.all().count()
        if app_count > 0:
            print(f"删除 {app_count} 个SocialApp对象")
            SocialApp.objects.all().delete()
        else:
            print("没有找到SocialApp对象")
        
        print("所有社交账号相关的对象已删除")
        return True
    except Exception as e:
        print(f"清理社交账号相关对象错误: {str(e)}")
        return False

def create_github_app():
    """
    创建GitHub应用配置
    """
    try:
        # 获取Site对象
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"Site: {site.domain}, {site.name}")
        
        # 检查是否已存在GitHub应用配置
        if SocialApp.objects.filter(provider='github').exists():
            print("已存在GitHub应用配置，跳过创建")
            return True
        
        # 创建新的GitHub应用配置
        if hasattr(settings, 'SOCIALACCOUNT_PROVIDERS') and 'github' in settings.SOCIALACCOUNT_PROVIDERS:
            github_config = settings.SOCIALACCOUNT_PROVIDERS['github']
            if 'APP' in github_config:
                app_config = github_config['APP']
                client_id = app_config.get('client_id', '')
                secret = app_config.get('secret', '')
                key = app_config.get('key', '')
                
                if client_id and secret:
                    github_app = SocialApp.objects.create(
                        provider='github',
                        name='GitHub',
                        client_id=client_id,
                        secret=secret,
                        key=key
                    )
                    github_app.sites.add(site)
                    print(f"已创建新的GitHub应用配置: ID={github_app.id}, Name={github_app.name}, Client ID={github_app.client_id}")
                    return True
                else:
                    print("Client ID或Secret为空，无法创建GitHub应用配置")
            else:
                print("settings中未找到GitHub APP配置")
        else:
            print("settings中未找到GitHub配置")
        return False
    except Exception as e:
        print(f"创建GitHub应用配置错误: {str(e)}")
        return False

def reset_github_app():
    """
    重置GitHub应用配置
    """
    try:
        # 清理所有社交账号相关的对象
        clean_social_apps()
        
        # 创建新的GitHub应用配置
        create_github_app()
        
        return True
    except Exception as e:
        print(f"重置GitHub应用配置错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 如果直接运行此文件，则重置GitHub应用配置
    reset_github_app()
