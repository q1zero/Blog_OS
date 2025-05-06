from django.db import models
from django.utils import timezone

# Create your models here.


class SensitiveWord(models.Model):
    word = models.CharField(max_length=100, unique=True, verbose_name="敏感词")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = "敏感词"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
