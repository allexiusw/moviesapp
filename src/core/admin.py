from django.contrib import admin

from core.models import Movie, MovieImage
# Register your models here.

class MovieImageInline(admin.TabularInline):
    model = MovieImage

class AdminMovie(admin.ModelAdmin):
    inlines = [MovieImageInline]

admin.site.register(Movie, AdminMovie)
