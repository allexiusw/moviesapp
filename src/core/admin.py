from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from core.models import Movie, MovieImage


class AtLeastOneImage(BaseInlineFormSet):
    '''Force to upload one image'''

    def clean(self):
        """Check that at least one image has been entered."""
        super(AtLeastOneImage, self).clean()
        if any(self.errors):
            return
        data = self.cleaned_data
        if not any(i and not i.get('DELETE', False) for i in data):
            raise forms.ValidationError('At least one item required.')


class MovieImageInline(admin.TabularInline):
    '''Define images movie as formset and force to have a least one image'''
    model = MovieImage
    formset = AtLeastOneImage


class AdminMovie(admin.ModelAdmin):
    '''Add the inline as modeladmin'''
    inlines = [MovieImageInline]


admin.site.register(Movie, AdminMovie)
