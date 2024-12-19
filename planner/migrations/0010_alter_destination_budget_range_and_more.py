# Generated by Django 5.1.4 on 2024-12-12 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0009_remove_destination_image_url_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="destination",
            name="budget_range",
            field=models.CharField(
                choices=[
                    ("low", "Low (Under Rs. 10000)"),
                    ("medium", "Medium (Rs. 10000-30000)"),
                    ("high", "High (Rs. 30000-80000)"),
                    ("luxury", "Luxury (Over Rs. 80000)"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="destination",
            name="category",
            field=models.CharField(
                choices=[
                    ("beach", "Beach"),
                    ("city", "City"),
                    ("mountains", "Mountains"),
                    ("historical", "Historical"),
                    ("adventure", "Adventure"),
                    ("cultural", "Cultural"),
                    ("nature", "Nature"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="destination",
            name="climate",
            field=models.CharField(
                choices=[
                    ("tropical", "Tropical"),
                    ("desert", "Desert"),
                    ("temperate", "Temperate"),
                    ("alpine", "Alpine"),
                    ("mediterranean", "Mediterranean"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="preferred_budget_range",
            field=models.CharField(
                blank=True,
                choices=[
                    ("low", "Low (Under Rs. 10000)"),
                    ("medium", "Medium (Rs. 10000-30000)"),
                    ("high", "High (Rs. 30000-80000)"),
                    ("luxury", "Luxury (Over Rs. 80000)"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="preferred_category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("beach", "Beach"),
                    ("city", "City"),
                    ("mountains", "Mountains"),
                    ("historical", "Historical"),
                    ("adventure", "Adventure"),
                    ("cultural", "Cultural"),
                    ("nature", "Nature"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="preferred_climate",
            field=models.CharField(
                blank=True,
                choices=[
                    ("tropical", "Tropical"),
                    ("desert", "Desert"),
                    ("temperate", "Temperate"),
                    ("alpine", "Alpine"),
                    ("mediterranean", "Mediterranean"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
