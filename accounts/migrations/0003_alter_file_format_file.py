# Generated by Django 4.1.13 on 2024-05-02 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_file_user_delete_customuser_file_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='format_file',
            field=models.CharField(max_length=180),
        ),
    ]
