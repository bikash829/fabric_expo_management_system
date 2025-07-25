# Generated by Django 5.0 on 2025-06-18 04:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_whatsapp', '0003_alter_whatsapptemplate_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsappSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(choices=[('processing', 'Processing'), ('done', 'Done'), ('failed', 'Failed')], default='processing', max_length=20)),
                ('success_count', models.PositiveIntegerField(default=0)),
                ('failure_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('draft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bulk_whatsapp.whatsapptemplate')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
