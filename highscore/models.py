from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User

class Registration(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

class Highscore(models.Model):
    player = models.ForeignKey(User)
    player_name = models.CharField(max_length=30)
    score = models.IntegerField()
    updated = models.DateTimeField(auto_now_add=True)

    def ranking(self):
        rs = Highscore.objects.filter(score__gt=self.score)
        return rs.aggregate(ranking=Count('score'))['ranking'] + 1

class Match(models.Model):
    player = models.ForeignKey(User)
    score = models.IntegerField()
    started = models.DateTimeField(auto_now_add=True)
    saved = models.DateTimeField(auto_now_add=True)
