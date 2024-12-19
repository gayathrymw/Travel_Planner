# Generated by Django 5.1.4 on 2024-12-13 15:28

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0011_delete_recommendationdata"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RecommendationData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                    ),
                ),
                (
                    "destination",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="planner.destination",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"unique_together": {("user", "destination")},},
        ),
    ]
