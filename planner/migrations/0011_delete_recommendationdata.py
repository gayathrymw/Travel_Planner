# Generated by Django 5.1.4 on 2024-12-13 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0010_alter_destination_budget_range_and_more"),
    ]

    operations = [
        migrations.DeleteModel(name="RecommendationData",),
    ]
