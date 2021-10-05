from django.utils.translation import gettext_lazy as _


class Messages(object):
    '''This class map the custom messages that will be rendered by
    the API in cases where user is performing an specific action'''

    MOVIE_AVAILABLE = _("Movie was changed to available.")
    MOVIE_UNAVAILABLE = _("Movie was changed to unavailable.")
