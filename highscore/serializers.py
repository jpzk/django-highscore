from django.contrib.auth.models import User, Group
from highscore.models import Registration, Match, Highscore
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class UserSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class HighscoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highscore
        fields = ('player_name', 'score',)

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match 

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration

