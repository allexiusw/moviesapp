from django import forms
from django.conf import settings
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.contrib.admin.models import LogEntry,  DELETION

from core.models import Movie, MovieImage, Purchase, Rent


if settings.DEBUG:

    class AtLeastOneImage(BaseInlineFormSet):
        '''Force to upload one image'''

        def clean(self) -> None:
            """Check that at least one image has been entered."""
            super(AtLeastOneImage, self).clean()
            if any(self.errors):
                return
            data = self.cleaned_data
            # check if action is delete or at least one image uploaded
            if not any(i and not i.get('DELETE', False) for i in data):
                raise forms.ValidationError('At least one item required.')
            return data

    class MovieImageInline(admin.TabularInline):
        '''Define images movie as formset and force to have at
            least one image'''
        model = MovieImage
        formset = AtLeastOneImage

    class AdminMovie(admin.ModelAdmin):
        '''Add the inline as modeladmin'''
        inlines = [MovieImageInline]

    class LogEntryAdmin(admin.ModelAdmin):
        list_display = [
            'action_time',
            'user',
            'content_type',
            'object_link',
            'action_flag',
        ]

        def object_link(self, obj) -> SafeString:
            '''Build the link to access to the item when was
                updated or edited'''
            if obj.action_flag == DELETION:
                link = escape(obj.object_repr)
            else:
                ct = obj.content_type
                link = '<a href="%s">%s</a>' % (
                            reverse(
                                f'admin:{ct.app_label}_{ct.model}_change',
                                args=[obj.object_id]),
                            escape(obj.object_repr),
                        )
            return mark_safe(link)

    admin.site.register(Movie, AdminMovie)
    admin.site.register(LogEntry, LogEntryAdmin)
    admin.site.register(Rent)
    admin.site.register(Purchase)
