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
    likes = models.ManyToManyField(User, verbose_name=_('Likes'))

    class Meta:
        verbose_name = _("Movie")
        verbose_name_plural = _("Movies")
        ordering = ('title',)

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.pk} - {self.title}'


class MovieImage(models.Model):
    '''Manage as many images per movie as required'''
    movie = models.ForeignKey(
        Movie, related_name='movies', on_delete=models.CASCADE)
    image = models.ImageField(_("Image"), upload_to='movies/images/')

    class Meta:
        verbose_name = _("Movie Image")
        verbose_name_plural = _("Movie Images")

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.pk} - {self.movie.title}'


def get_due_date(days=7) -> datetime:
    '''Return the due day which will be 7 later from now'''
    return (datetime.now()+timedelta(days=days)).date


class Rent(models.Model):
    '''Manage Rent entity and its fields'''

    rented_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    due_date = models.DateField(_("Due Date"))
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"))
    returned = models.BooleanField(_("Is Returned"), default=False)
    returned_at = models.DateField(_("Returned At"), blank=True, null=True)
    is_paid = models.BooleanField(_("Is paid?"), default=False)
    paid_at = models.DateTimeField(_("Paid at"), blank=True, null=True)
    amount = models.DecimalField(_("Amount"), max_digits=8, decimal_places=2)
    payment_reference = models.CharField(
        _("Payment reference"), max_length=100, blank=True, null=True)
    payment_url = models.URLField(
        _("Payment url"), blank=True, null=True)

    class Meta:
        verbose_name = _("Rent")
        verbose_name_plural = _("Rents")

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.pk} - {self.movie.title}'


class ExtraCharge(models.Model):
    '''Manage extra charges when returning movies'''
    created_at = models.DateField(auto_now_add=True)
    amount = models.DecimalField(
        _("Amount"), max_digits=8, decimal_places=2, default=0.0)
    is_paid = models.BooleanField(_("Is paid?"), default=False)
    paid_at = models.DateTimeField(_("Paid at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Extra charge")
        verbose_name_plural = _("Extra charges")

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.pk} - {self.movie.title}'


class Sale(models.Model):
    '''Manage the movies sold to the Clients'''
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    date = models.DateTimeField(_("Date"))
    amount = models.DecimalField(_("Amount"), max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")

    def __str__(self) -> str:
        '''Return the representation of each row'''
        return f'{self.movie} - {self.amount}'
