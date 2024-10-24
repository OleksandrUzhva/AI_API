# Generated by Django 5.1.2 on 2024-10-21 16:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="is_blocked",
            field=models.DurationField(default=False),
        ),
        migrations.AlterField(
            model_name="post",
            name="auto_reply_enabled",
            field=models.DurationField(default=False),
        ),
    ]