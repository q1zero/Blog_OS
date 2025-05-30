# Generated by Django 4.2.20 on 2025-05-06 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, verbose_name="创建时间"
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="is_approved",
            field=models.BooleanField(
                db_index=True, default=False, verbose_name="是否审核通过"
            ),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(
                fields=["article", "is_approved"], name="article_approved_idx"
            ),
        ),
    ]
