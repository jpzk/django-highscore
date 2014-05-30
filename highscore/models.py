from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Registration(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

class Highscore(models.Model):
    pk = models.ForeignKey(User)
    score = models.IntegerField()
    updated = models.DateTimeField(auto_now_add=True)

class Match(models.Model):
    player = models.ForeignKey(User)
    score = models.IntegerField()
    started = models.DateTimeField(auto_now_add=True)
    saved = models.DateTimeField(auto_now_add=True)
