from django.utils.translation import gettext_lazy as _


class Messages(object):
    '''This class map the custom messages that will be rendered by
    the API in cases where user is performing an specific action'''

    MOVIE_AVAILABLE = _("Movie was changed to available.")
    MOVIE_UNAVAILABLE = _("Movie was changed to unavailable.")
    RENT_QUANTITY_LOW = _("Rent quantity too low")
    RENT_QUANTITY_NOT_AVAI = _("Rent quantity not available")
    RENT_SUCCESSFULLY = _("Rent successfully")
    MOVIE_BUYED = _("Movie buyed successfully")
    DUE_DATE_TOO_LONG = _("Due date too low")
