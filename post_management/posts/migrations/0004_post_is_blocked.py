# Generated by Django 5.1.2 on 2024-10-21 16:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0003_alter_comment_is_blocked_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="is_blocked",
            field=models.BooleanField(default=False),
        ),
    ]
