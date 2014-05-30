django-highscore
================

Simple Django Rest API for Highscores

Installation
============

Add this to your settings.py of your Django project.

..code-block::python

    REST_FRAMEWORK = {
        # Use hyperlinked styles by default.
        # Only used if the `serializer_class` attribute is not set on a view.
        'DEFAULT_AUTHENTICATION_CLASSES': 
            ('rest_framework.authentication.TokenAuthentication',),
    
        # Use Django's standard `django.contrib.auth` permissions,
        # or allow read-only access for unauthenticated users.
        'DEFAULT_PERMISSION_CLASSES': 
        ('rest_framework.permissions.IsAdminUser',) 
    }
    
    INSTALLED_APPS = (
        ...
        'rest_framework',
        'rest_framework.authtoken',
        'highscore'
    )
    
    
