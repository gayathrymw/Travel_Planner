# Generated by Django 5.1.4 on 2024-12-13 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0012_recommendationdata"),
    ]

    operations = [
        migrations.RemoveField(model_name="recommendationdata", name="rating",),
        migrations.DeleteModel(name="WeatherData",),
    ]
