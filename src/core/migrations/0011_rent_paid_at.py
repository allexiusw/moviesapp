# Generated by Django 3.2.7 on 2021-10-10 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20211010_0333'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='paid_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Paid at'),
        ),
    ]