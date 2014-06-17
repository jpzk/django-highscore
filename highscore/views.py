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
    """Allow registration, to create new users.

    Default API endpoint: /registration/,
    url(r'^registration/$', views.RegistrationView.as_view())"""

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
    """Return the count of highscores (greater than 0) and
    the amount of pages.

    Default API endpoint: /highscores/,
    url(r'^highscores/$', views.HighscoreCountView.as_view())"""

    permission_classes = ()
    def get(self, request):
        count = Highscore.objects.filter(score__gt = 0).count()
        payload = {'count' : count,
                   'pages' : int(ceil(count / 10.0))}
        return Response(payload)

class HighscorePagesView(APIView):
    """Return the global highscore list in pages.

    Default API endpoint: /highscores/0/
    url(r'^highscores/(?P<page>[0-9]*)/$', views.HighscorePage)"""

    permission_classes = ()
    def get(self, request, page):
        start = 10 * int(page)
        end = start + 10
        greater_zero = Highscore.objects.filter(score__gt = 0)
        highscores = greater_zero.order_by('score').reverse()[start:end]
        serializer = HighscoreSerializer(highscores, many=True)
        return Response(serializer.data)

class UserHighscoreView(APIView):
    """Return the player highscore.

    Default API endpoint: /user/highscore/
    url(r'^user/highscore/$', views.UserHighscoreView.as_view()"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Get the player highscore"""

        highscore = Highscore.objects.get(player=request.user.id)
        serializer = HighscoreSerializer(highscore)

        # Adding ranking to the data
        resp_data = serializer.data
        resp_data['rank'] = highscore.ranking() # TODO cache
        return Response(resp_data)

class UserMatchView(APIView):
    """Return the matches of a player.

    Default API endpoint: /user/matches/
    url(r'^user/highscore/$', views.UserHighscoreView.as_view())"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Submit a match."""

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
        """Get a list of matches of player."""

        matches = Match.objects.filter(player=request.user.id)
        serializer = MatchSerializer(matches)
        return Response(serializer.data)

class UserView(APIView):
    """Get user-specific details.

    Default API endpoint: /user/,
    url(r'^user/$', views.UserView.as_view())"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        serializer = UserSingleSerializer(user)
        return Response(serializer.data)

"""
# Following views only for administrators.

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'matches', views.MatchViewSet)
router.register(r'highscores', views.HighscoreViewSet)

...
url(r'^data/', include(router.urls)),
...
"""

class HighscoreViewSet(viewsets.ModelViewSet):
    """Highscore View Set, @see ModelViewSet"""

    queryset = Highscore.objects.all()
    serializer_class = HighscoreSerializer

class MatchViewSet(viewsets.ModelViewSet):
    """Match View Set, @see ModelViewSet"""

    queryset = Match.objects.all()
    serializer_class = MatchSerializer

class UserViewSet(viewsets.ModelViewSet):
    """User View Set, @see ModelViewSet"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """Group View Set, @see ModelViewSet"""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
