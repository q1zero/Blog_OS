from django.http import JsonResponse


class HealthCheckMiddleware:
    """
    中间件，用于处理Replit部署健康检查
    这个中间件会检测来自部署健康检查的请求，并返回成功响应
    而不干扰正常用户的访问
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查是否是健康检查请求
        user_agent = request.headers.get("User-Agent", "").lower()

        # 如果是来自Replit的健康检查请求，并且访问根路径
        if (
            "replit" in user_agent or "health-check" in user_agent
        ) and request.path == "/":
            return JsonResponse({"status": "ok", "message": "服务正常运行"})

        # 其他请求正常处理
        response = self.get_response(request)
        return response
