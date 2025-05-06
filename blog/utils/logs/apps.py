from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "utils.logs"
    verbose_name = _("访问日志")
