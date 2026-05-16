from django.db import models


class Jewelry(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='jewelry/', blank=True, null=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Banner(models.Model):
    BANNER_CHOICES = [
        ('top', 'Top Banner'),
        ('bottom1', 'Bottom Banner 1'),
        ('bottom2', 'Bottom Banner 2'),
        ('bottom3', 'Bottom Banner 3'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    banner_type = models.CharField(max_length=20, choices=BANNER_CHOICES, default='top')
    image = models.ImageField(upload_to='banners/', blank=True, null=True)

    def __str__(self):
        return self.title