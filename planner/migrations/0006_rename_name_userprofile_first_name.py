# Generated by Django 5.1.4 on 2024-12-10 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0005_userprofile_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userprofile", old_name="name", new_name="first_name",
        ),
    ]
