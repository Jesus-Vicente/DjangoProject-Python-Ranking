from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings
from django_mongodb_backend.fields import EmbeddedModelField, ArrayField
from django_mongodb_backend.models import EmbeddedModel

class Character(EmbeddedModel):
    code = models.IntegerField(null=False, unique=True)
    firstName = models.CharField(max_length=150)
    lastName = models.CharField(max_length=150)
    fullName = models.CharField(max_length=300)

    image = models.CharField(max_length=300)
    imageUrl = models.CharField(max_length=1000)
    category = ArrayField(models.IntegerField(), null=True, blank=True, default=list)

    class Meta:
        db_table = ('characters')
        managed = False

    def __str__(self):
        return self.fullName

class Category(EmbeddedModel):
    code = models.IntegerField(null=False)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=300)

    class Meta:
        db_table = ('categories')

class Review(EmbeddedModel):
    user = models.CharField(max_length=300)
    characterCode = models.IntegerField(null=False)
    reviewDate = models.DateField()
    rating = models.PositiveIntegerField(null=False, validators=[MinValueValidator(0), MaxValueValidator(5)])
    comments = models.TextField()

    def __str__(self):
        return self.user + " " + str(self.rating)

    class Meta:
        db_table = ('reviews')
        managed = False

class Raking(EmbeddedModel):
    user = models.CharField(max_length=300)
    rankingDate = models.DateField()
    categoryCode = models.IntegerField(null=False)
    rankingList = ArrayField(models.IntegerField(), null=True, blank=True, default=list)
