# Generated by Django 5.0.3 on 2024-12-15 15:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookingApk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unavailability',
            name='screen',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unavailabilities', to='BookingApk.screen'),
        ),
    ]