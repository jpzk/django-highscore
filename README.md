django-highscore
================

**Simple Django REST JSON API for Highscores** with OAuth2 authorization. **Important**: In production environment use HTTPS!

Examples
========

Get first page of highscore list, ordered best score first.

    curl -X GET http:s//localhost:8000/highscores/0/

Register new users on /registration/ 

    curl -X POST -d 'username=jpzk&password=yourguess'\
    https://localhost:8000/registration/

Get OAuth2 token for user jpzk, which identifies the user:

    curl -X POST -d 'username=jpzk&password=yourguess&grant_type=password&client_id=jpzk'\
    https://localhost:8000/oauth2/access_token/

Send match score for user jpzk (highscore is updated when score is greater than the old score):

    curl -X POST -H 'Authorization: bearer <token>' -d 'score=100'\
    https://localhost:8000/user/matches/

Get ranking of user jpzk:

    curl -X GET -H 'Authorization: bearer <token>'\
    https://localhost:8000/user/highscore/ 

Requirements
============

It is tested with the following versions. Add the missing packages to the requirements.txt of your Django project 

    django==1.6
    django_oauth2_provider==0.2.6.1
    djangorestframework==2.3.13
    markdown==2.4.1
    django-filter==0.7
    
Installation
============

Add this to your settings.py of your Django project.

    REST_FRAMEWORK = {
        # Use hyperlinked styles by default.
        # Only used if the `serializer_class` attribute is not set on a view.
 
        'DEFAULT_AUTHENTICATION_CLASSES': 
            ('rest_framework.authentication.OAuth2Authentication',
            'rest_framework.authentication.SessionAuthentication'),

        # Use Django's standard `django.contrib.auth` permissions,
        # or allow read-only access for unauthenticated users.
        'DEFAULT_PERMISSION_CLASSES': 
        ('rest_framework.permissions.IsAdminUser',) 
    }
    
    INSTALLED_APPS = (
        ...
        'provider',
        'provider.oauth2',
        'rest_framework',
        'highscore'
    )
    
Modify your urls.py accordingly:

    from django.conf.urls import patterns, include, url
    from django.contrib.auth.models import User, Group
    from rest_framework import viewsets, routers
    from highscore import views
    import rest_framework
    
    router = routers.DefaultRouter()
    router.register(r'users', views.UserViewSet)
    router.register(r'groups', views.GroupViewSet)
    router.register(r'matches', views.MatchViewSet)
    router.register(r'highscores', views.HighscoreViewSet)
    
    urlpatterns = patterns('',
        # Admin views
        url(r'^data/', include(router.urls)),
        url(r'^data/highscores', views.HighscorePagesView.as_view()),
    
        # Anonymous views
        url(r'^registration/$', views.RegistrationView.as_view()),
        url(r'^highscores/$', views.HighscoreCountView.as_view()),
    
        url(r'^highscores/(?P<page>[0-9]*)/$', views.HighscorePagesView.as_view()),
        # User-specific views
        url(r'^user/matches/$', views.UserMatchView.as_view()),
        url(r'^user/highscore/$', views.UserHighscoreView.as_view()),
        url(r'^user/$', views.UserView.as_view()),
        
        # API authentification
        url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    )  
