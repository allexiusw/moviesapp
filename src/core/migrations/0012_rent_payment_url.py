# Generated by Django 3.2.7 on 2021-10-10 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_rent_paid_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='payment_url',
            field=models.URLField(
                blank=True, null=True, verbose_name='Payment reference'),
        ),
    ]
