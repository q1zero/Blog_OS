from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from .models import AccessLog


def apply_migrations(request):
    """临时视图，用于应用迁移"""
    try:
        # 创建表
        with connections['default'].cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "logs_accesslog" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "path" varchar(255) NOT NULL,
                "method" varchar(10) NOT NULL,
                "status_code" integer NULL,
                "ip_address" char(39) NULL,
                "user_agent" text NOT NULL,
                "referer" varchar(255) NOT NULL,
                "query_params" text NOT NULL,
                "response_time" real NULL,
                "timestamp" datetime NOT NULL,
                "user_id" integer NULL REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED
            )
            """)

            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS "logs_access_timesta_e6f0cd_idx" ON "logs_accesslog" ("timestamp")')
            cursor.execute('CREATE INDEX IF NOT EXISTS "logs_access_user_id_d7a6fa_idx" ON "logs_accesslog" ("user_id")')
            cursor.execute('CREATE INDEX IF NOT EXISTS "logs_access_path_d7a6fa_idx" ON "logs_accesslog" ("path")')
            cursor.execute('CREATE INDEX IF NOT EXISTS "logs_access_status__d7a6fa_idx" ON "logs_accesslog" ("status_code")')

        return HttpResponse("迁移已成功应用！请返回管理界面。")
    except Exception as e:
        return HttpResponse(f"应用迁移时出错：{e}")


@staff_member_required
def access_log_dashboard(request):
    """访问日志仪表盘，仅管理员可见"""
    # 获取所有日志
    logs = AccessLog.objects.all()

    # 分页
    paginator = Paginator(logs, 20)  # 每页显示20条日志
    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)

    # 统计信息
    total_logs = AccessLog.objects.count()
    total_users = AccessLog.objects.filter(user__isnull=False).values('user').distinct().count()
    total_anonymous = AccessLog.objects.filter(user__isnull=True).count()

    # 状态码统计
    status_codes = AccessLog.objects.values('status_code').distinct()
    status_stats = {}
    for code in status_codes:
        code_value = code['status_code']
        if code_value:
            count = AccessLog.objects.filter(status_code=code_value).count()
            status_stats[code_value] = count

    context = {
        'logs': logs,
        'total_logs': total_logs,
        'total_users': total_users,
        'total_anonymous': total_anonymous,
        'status_stats': status_stats,
        'title': _('访问日志仪表盘'),
    }

    return render(request, 'logs/dashboard.html', context)
