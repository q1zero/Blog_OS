import time
import json
from django.utils.deprecation import MiddlewareMixin
from .models import AccessLog


class AccessLogMiddleware(MiddlewareMixin):
    """
    访问日志中间件，记录所有HTTP请求的信息
    
    记录内容包括：
    - 请求路径、方法和状态码
    - 用户信息（如果已登录）
    - IP地址和用户代理
    - 来源页面
    - 查询参数
    - 响应时间
    """
    
    def process_request(self, request):
        """处理请求，记录开始时间"""
        request.start_time = time.time()
    
    def process_response(self, request, response):
        """处理响应，记录访问日志"""
        # 计算响应时间（毫秒）
        if hasattr(request, 'start_time'):
            response_time = (time.time() - request.start_time) * 1000
        else:
            response_time = None
        
        # 获取用户（如果已登录）
        user = request.user if request.user.is_authenticated else None
        
        # 获取IP地址
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # 获取查询参数
        query_params = {}
        if request.GET:
            query_params = dict(request.GET)
        
        # 过滤掉静态文件和管理员请求
        path = request.path
        if path.startswith('/static/') or path.startswith('/media/'):
            return response
        
        # 创建访问日志记录
        try:
            AccessLog.objects.create(
                path=path,
                method=request.method,
                status_code=response.status_code,
                user=user,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referer=request.META.get('HTTP_REFERER', ''),
                query_params=json.dumps(query_params) if query_params else '',
                response_time=response_time
            )
        except Exception as e:
            # 记录日志失败不应影响正常响应
            print(f"记录访问日志失败: {e}")
        
        return response
