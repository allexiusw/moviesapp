from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.forms import forms

from core.models import Movie, MovieImage


class AtLeastOneImage(BaseInlineFormSet):
    '''Force to upload one image'''

    def clean(self):
        """Check that at least one image has been entered."""
        super(AtLeastOneImage, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False)
            for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('At least one item required.')


class MovieImageInline(admin.TabularInline):
    '''Define images movie as formset inline and force to have a least one images'''
    model = MovieImage
    formset = AtLeastOneImage


class AdminMovie(admin.ModelAdmin):
    '''Add the inline as modeladmin'''
    inlines = [MovieImageInline]


admin.site.register(Movie, AdminMovie)
