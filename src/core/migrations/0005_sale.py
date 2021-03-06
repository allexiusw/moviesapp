# Generated by Django 3.2.7 on 2021-10-02 20:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_auto_20211002_1821'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Created At')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('amount', models.DecimalField(
                    decimal_places=2, max_digits=6, verbose_name='Amount')),
                ('movie', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='core.movie')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Sale',
                'verbose_name_plural': 'Sales',
            },
        ),
    ]
