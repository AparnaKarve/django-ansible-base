# Generated by Django 4.2.8 on 2024-04-15 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0008_secretcolor'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.CharField(editable=False, max_length=100, null=True),
        ),
    ]
