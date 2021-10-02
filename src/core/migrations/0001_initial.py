# Generated by Django 3.2.7 on 2021-10-02 04:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('title', models.CharField(
                    max_length=200, verbose_name='Title')),
                ('description', models.TextField(
                    max_length=500, verbose_name='Description')),
                ('stock', models.IntegerField(verbose_name='Stock')),
                ('rental_price', models.DecimalField(
                    decimal_places=2,
                    max_digits=8,
                    verbose_name='Rental Price')),
                ('sale_price', models.DecimalField(
                    decimal_places=2,
                    max_digits=8,
                    verbose_name='Sale Price')),
                ('availability', models.BooleanField(
                    default=True, verbose_name='Is available')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(
                    auto_now=True, verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Movie',
                'verbose_name_plural': 'Movies',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='MovieImage',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('image', models.ImageField(
                    upload_to='media/movies/images/',
                    verbose_name='Image')),
                ('movie', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='core.movie')),
            ],
            options={
                'verbose_name': 'Movie Image',
                'verbose_name_plural': 'Movie Images',
            },
        ),
    ]
