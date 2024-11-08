# Generated by Django 5.1.1 on 2024-11-04 20:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube_link', models.URLField()),
                ('processing_speed', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending', max_length=10)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
