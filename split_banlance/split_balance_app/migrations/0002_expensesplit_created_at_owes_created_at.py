# Generated by Django 4.2.6 on 2023-10-19 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('split_balance_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensesplit',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='owes',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
