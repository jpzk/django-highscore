from StringIO import StringIO

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from highscore.models import Match, Highscore, Registration
from highscore.serializers import HighscoreSerializer

class UserAPITestCase(APITestCase):

    user1 = {'username':'test-user-1', 'password':'test-pass'}
    user2 = {'username':'test-user-2', 'password':'test-pass'}

    def get_user(self, cred):
        return User.objects.get(username=cred['username'])

    def register(self, cred):
        response = self.client.post('/registration/', cred)
        return response

    def get_token(self, cred):
        response = self.client.post('/api-auth-token/', cred)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

class RegistrationTest(UserAPITestCase):

    def test_register(self):
        """ Register a user acccount. """
    
        response = self.register(self.user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_token(self):
        """ Register, get token """

        self.register(self.user1)
        self.get_token(self.user1)

    def test_register_login(self):
        """ Register and login with a user account. """

        self.register(self.user1)
        self.get_token(self.user1)
        
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

class HighscoresTest(UserAPITestCase):

    def submit_match(self, score):
        data = {'score': score }
        response = self.client.post('/user/matches/', data)
        return response

    def test_submit_multiple_matches(self):
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match(1)
        response = self.submit_match(2)

        # Assert highscore update
        highscore = Highscore.objects.get(pk = self.get_user(self.user1).id)
        self.assertTrue(highscore.score == 2)

    def test_get_highscore(self):
        self.register(self.user1)
        self.get_token(self.user1)
        self.submit_match(1)
        response = self.client.get('/user/highscore/')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertEqual(response.data['score'], 1)

    def test_highscores(self):
        self.register(self.user1)
        self.get_token(self.user1)
        self.submit_match(1)
        self.register(self.user2)
        self.get_token(self.user2)
        self.submit_match(2)

        # logout
        self.client.credentials()

        response = self.client.get('/highscores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertTrue(len(response.data) == 2) 

class MatchSubmissionHighscoreTest(UserAPITestCase):

    def submit_match(self):
        data = {'score': 123456 }
        response = self.client.post('/user/matches/', data)
        return response

    def test_submit_match_with_login(self):
        """ Submit match data """
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert match object creation
        matches = Match.objects.filter(player = self.get_user(self.user1))
        self.assertTrue(matches[0].score == 123456)

    def test_submit_match_creation(self):
        """ Submit match data """
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert match object creation
        matches = Match.objects.filter(player = self.get_user(self.user1))
        self.assertTrue(matches[0].score == 123456)

    def test_submit_highscore_update(self):
        """ Submit match data """
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert highscore update
        highscore = Highscore.objects.get(pk = self.get_user(self.user1).id)
        self.assertTrue(highscore.score == 123456)

    def test_submit_match_without_login(self):
        response = self.submit_match()
        self.assertEqual(response.status_code, 401)

