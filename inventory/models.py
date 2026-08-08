from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class Jewelry(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='jewelry_images/', null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            old = Jewelry.objects.filter(pk=self.pk).first()
            image_changed = old is None or old.image != self.image
        else:
            image_changed = bool(self.image)

        if self.image and image_changed:
            img = Image.open(self.image)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img = img.resize((300, 300))
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            self.image = ContentFile(buffer.read(), name=self.image.name)

        super().save(*args, **kwargs)


class Comment(models.Model):
    item = models.ForeignKey(Jewelry, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class Like(models.Model):
    item = models.ForeignKey(Jewelry, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user.username}"


class Banner(models.Model):
    ...
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.thumbnail((1600, 1600))  # cap max dimension, keep aspect ratio
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            self.image = ContentFile(buffer.read(), name=self.image.name)
        super().save(*args, **kwargs)