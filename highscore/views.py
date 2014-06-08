from django.shortcuts import render
from django.contrib.auth.models import User, Group
from provider.oauth2.models import Client

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from highscore.models import Match, Highscore
from highscore.serializers import HighscoreSerializer
from highscore.serializers import RegistrationSerializer 
from highscore.serializers import MatchSerializer
from highscore.serializers import UserSerializer, GroupSerializer
from highscore.serializers import UserSingleSerializer

# Anonymous Views

class RegistrationView(APIView):
    """ Allow registration as anonymous user. """
        
    permission_classes = ()
    def post(self, request, format=None):
        serializer = RegistrationSerializer(data=request.DATA)
        if serializer.is_valid():

            # Create a user and set highscore to 0.
            data = serializer.data
            u = User.objects.create(username=data['username'])
            u.set_password(data['password'])
            u.save()

            # Create OAuth2 client
            name = u.username
            client = Client(user=u, name=name, url='highscore://' + name,\
                    client_id=name, client_secret='', client_type=1)
            client.save()

            # Setting the initial highscore to 0.
            Highscore.objects.create(player=u, score=0)

            created = status.HTTP_201_CREATED
            return Response(serializer.data, status=created)
        bad_request = status.HTTP_400_BAD_REQUEST
        return Reponse(serializer.errors, status=bad_request)

class HighscoreView(APIView):
    """ See the global highscore list """
    
    permission_classes = ()
    def get(self, request):
        highscores = Highscore.objects.all()
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

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
