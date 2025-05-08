"""
GitHub认证测试URL
"""
from django.http import HttpResponse

def test_urls(request):
    """
    简化的测试视图
    """
    try:
        # 构建简化的响应
        response = """
        <h1>GitHub认证测试</h1>
        <p>该页面用于测试GitHub认证功能。</p>
        <p>当前使用的是自定义的GitHub登录流程，不需要测试不同的回调URL格式。</p>
        
        <h2>使用方法</h2>
        <p>点击登录页面上的"使用GitHub登录"按钮，即可使用GitHub账号登录系统。</p>
        """
        
        return HttpResponse(response)
    except Exception as e:
        return HttpResponse(f"<h1>错误</h1><p>{str(e)}</p>")
