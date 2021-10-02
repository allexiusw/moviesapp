from datetime import datetime, timedelta

from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class Movie(models.Model):
    '''Define de base structure of the Movie entity'''
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), max_length=500)
    stock = models.IntegerField(_("Stock"))
    rental_price = models.DecimalField(
        _("Rental Price"), max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(
        _("Sale Price"), max_digits=8, decimal_places=2)
    availability = models.BooleanField(_("Is available"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Created At"), auto_now=True)

    class Meta:
        verbose_name = _("Movie")
        verbose_name_plural = _("Movies")
        ordering = ('title',)

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.pk} - {self.title}'


class MovieImage(models.Model):
    '''Manage as many images per movie as required'''
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    image = models.ImageField(_("Image"), upload_to='media/movies/images/')

    class Meta:
        verbose_name = _("Movie Image")
        verbose_name_plural = _("Movie Images")

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.pk} - {self.movie.title}'


def get_due_date(days=7) -> datetime:
    '''Return the due day which will be 7 later from now'''
    return datetime.now()+timedelta(days=days)


class Rent(models.Model):
    '''Manage Rent entity and its fields'''

    rented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    due_date = models.DateField(_("Due Date"), default=get_due_date)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"))
    returned = models.BooleanField(_("Is Returned"), default=False)
    returned_at = models.DateTimeField(_("Returned At"), blank=True, null=True)
    extra_charge = models.DecimalField(
        _("Extra Charge"), max_digits=6, decimal_places=2, default=0.0)
    amount = models.DecimalField(_("Amount"), max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = _("Rent")
        verbose_name_plural = _("Rents")

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.pk} - {self.movie.title}'


class Purchase(models.Model):
    '''This entity will save all the rent purchases'''
    rent = models.OneToOneField(Rent, on_delete=models.CASCADE)
    date = models.DateTimeField(_("Date"), default=datetime.now)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    total = models.DecimalField(_("Total"), max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.date} - {self.rent} - {self.total}'
