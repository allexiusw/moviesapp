# Generated by Django 3.2.7 on 2021-10-05 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_movieimage_movie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='total',
            field=models.DecimalField(
                decimal_places=2, max_digits=8, verbose_name='Total'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='amount',
            field=models.DecimalField(
                decimal_places=2, max_digits=8, verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='extra_charge',
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=8,
                verbose_name='Extra Charge'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='amount',
            field=models.DecimalField(
                decimal_places=2, max_digits=8, verbose_name='Amount'),
        ),
    ]
