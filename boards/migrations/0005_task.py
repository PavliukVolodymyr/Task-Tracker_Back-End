# Generated by Django 3.2.23 on 2023-12-22 12:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('boards', '0004_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=10)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_tasks', to=settings.AUTH_USER_MODEL)),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='boards.list')),
            ],
        ),
    ]
