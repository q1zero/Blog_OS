from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


def health_check(request):
    """
    健康检查视图，用于部署环境的健康检查
    根据请求类型返回不同响应：
    - Accept: application/json 时返回JSON响应
    - 健康检查路径返回简单的HTML响应
    - 根路径则使用JavaScript自动跳转到文章列表
    """
    # 检查请求头是否接受JSON响应
    accept_header = request.headers.get("Accept", "")

    # 请求路径
    path = request.path

    # 如果是API请求或明确要求健康检查端点
    if "application/json" in accept_header or path in [
        "/health/",
        "/.well-known/health/",
    ]:
        return JsonResponse({"status": "ok", "message": "服务正常运行"})

    # 如果是健康检查请求，但不是API请求，返回简单的HTML响应
    if path in ["/health/", "/.well-known/health/"]:
        return HttpResponse("<h1>服务正常运行</h1>")

    # 如果请求来自Replit部署健康检查（识别特定的User-Agent或IP范围）
    user_agent = request.headers.get("User-Agent", "").lower()
    if "replit" in user_agent or "health-check" in user_agent:
        return JsonResponse({"status": "ok", "message": "服务正常运行"})

    # 其他情况，重定向到文章列表页（不再处理根路径）
    return redirect("articles:article_list")
