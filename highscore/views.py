from math import ceil
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from provider.oauth2.models import Client

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from highscore.errors import response, Error
from highscore.models import Match, Highscore
from highscore.serializers import HighscoreSerializer
from highscore.serializers import RegistrationSerializer 
from highscore.serializers import MatchSerializer
from highscore.serializers import UserSerializer, GroupSerializer
from highscore.serializers import UserSingleSerializer

class RegistrationView(APIView):
    """ Allow registration as anonymous user. """
        
    permission_classes = ()
    def post(self, request, format=None):
        serializer = RegistrationSerializer(data=request.DATA)
        bad_request = status.HTTP_400_BAD_REQUEST

        if not serializer.is_valid():
            return Response(serializer.errors, status=bad_request)
        else:
            data = serializer.data
            username = data['username']

            # Check if unique
            if User.objects.filter(username=username).exists():
                return Response(response(Error.USERNAME_TAKEN), 
                        bad_request)

            u = User.objects.create(username=data['username'])
            u.set_password(data['password'])
            u.save()

            # Create OAuth2 client
            name = u.username
            client = Client(user=u, name=name, url='' + name,\
                    client_id=name, client_secret='', client_type=1)
            client.save()

            # Setting the initial highscore to 0.
            Highscore.objects.create(player=u, player_name=u.username, score=0)

            created = status.HTTP_201_CREATED
            return Response(serializer.data, status=created)

class HighscoreCountView(APIView):
    permission_classes = ()
    def get(self, request):
        count = Highscore.objects.count()
        payload = {'count' : count,
                   'pages' : int(ceil(count / 10.0))}
        return Response(payload)

class HighscorePagesView(APIView):
    """ See the global highscore list in pages"""
    
    permission_classes = ()
    def get(self, request, page):
        start = 10 * int(page)
        end = start + 10
        highscores = Highscore.objects.order_by('score').reverse()[start:end]
        serializer = HighscoreSerializer(highscores, many=True)
        return Response(serializer.data)

# User-specific views

class UserHighscoreView(APIView):
    """ See the player highscore. """
        
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        highscore = Highscore.objects.get(player=request.user.id)
        serializer = HighscoreSerializer(highscore)
        return Response(serializer.data)

class UserMatchView(APIView):
    """ Matches """
        
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        u = request.DATA
        score = int(u['score'])
        m = Match(player=request.user, score=score)
        m.save()

        # Update the highscore, if score higher than highscore. 
        highscore = Highscore.objects.get(player=request.user.id)
        if score > highscore.score:
            highscore.score = score
        highscore.save()

        return Response("", status=status.HTTP_201_CREATED)

    def get(self, request):
        matches = Match.objects.filter(player=request.user.id)
        serializer = MatchSerializer(matches)
        return Response(serializer.data)

class UserView(APIView):
    """ User specific information """
        
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        serializer = UserSingleSerializer(user) 
        return Response(serializer.data)

# Only for admins, under /data/

class HighscoreViewSet(viewsets.ModelViewSet):
    queryset = Highscore.objects.all()
    serializer_class = HighscoreSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
