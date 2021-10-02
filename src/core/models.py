from django.db import models
from django.utils.translation import gettext as _


class Movie(models.Model):
    '''Define de base structure of the Movie entity'''
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), max_length=500)
    stock = models.IntegerField(_("Stock"))
    rental_price = models.DecimalField(_("Rental Price"), max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(_("Sale Price"), max_digits=8, decimal_places=2)
    availability = models.BooleanField(_("Is available"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Created At"), auto_now=True)

    class Meta:
        verbose_name = _("Movie")
        verbose_name_plural = _("Movies")
        ordering = ('title',)

    def __str__(self):
        '''Return the representation of each row'''
        return f'{self.pk} - {self.title}'

class MovieImage(models.Model):
    '''Manage as many images per movie as required'''
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    image = models.ImageField(_("Image"), upload_to='media/movies/images/')

    class Meta:
        verbose_name = _("Movie Image")
        verbose_name_plural = _("Movie Images")
    
    def __str__(self):
        '''Return the representation of each row'''
        return f'{self.pk} - {self.movie.title}'
