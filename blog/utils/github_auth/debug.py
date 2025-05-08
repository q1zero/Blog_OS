"""
GitHub认证调试工具
"""
from django.http import HttpResponse

def debug_redirect_uri(request):
    """
    调试重定向URI
    """
    try:
        # 构建简化的响应
        response = f"""
        <h1>GitHub认证调试</h1>
        <p>该页面用于调试GitHub认证功能。</p>
        <p>当前使用的是自定义的GitHub登录流程，不需要调试重定向URI。</p>
        
        <h2>请求信息</h2>
        <p>请求路径: {request.path}</p>
        <p>请求方法: {request.method}</p>
        <p>请求主机: {request.get_host()}</p>
        <p>请求协议: {'https' if request.is_secure() else 'http'}</p>
        """
        
        return HttpResponse(response)
    except Exception as e:
        return HttpResponse(f"<h1>错误</h1><p>{str(e)}</p>")
