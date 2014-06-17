from json import loads
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from highscore.errors import Error
from highscore.models import Match, Highscore

class UserAPITestCase(APITestCase):
    """This test case offers user fixtures and user methods"""

    user1 = {'username':'test-user-1', 'password':'test-pass'}
    user2 = {'username':'test-user-2', 'password':'test-pass'}

    def get_user(self, cred):
        return User.objects.get(username=cred['username'])

    def register(self, cred):
        response = self.client.post('/registration/', cred)
        return response

    def get_token(self, cred):
        data = {'grant_type':'password', 'username':cred['username'],\
        'password':cred['password'], 'client_id':cred['username']}

        response = self.client.post('/oauth2/access_token', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = loads(response.content)

        self.assertTrue('access_token' in response_data)
        token = response_data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

class RegistrationTest(UserAPITestCase):
    """Testing the registration of new users and login"""

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

class ErrorTest(UserAPITestCase):
    """Testing the error cases e.g. when username is taken"""

    def test_username_taken(self):
        response1 = self.register(self.user1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.register(self.user1)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        error_code = Error.USERNAME_TAKEN
        import pdb; pdb.set_trace()

        self.assertEqual(response2.data['error'], str(error_code))

class HighscoresTest(UserAPITestCase):
    """Testing submitting matches, submitting multiple matches,
       getting the highscore list, pages and player highscore"""

    def submit_match(self, score):
        data = {'score': score}
        response = self.client.post('/user/matches/', data)
        return response

    def test_submit_multiple_matches(self):
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match(1)
        response = self.submit_match(2)

        # Assert highscore update
        highscore = Highscore.objects.get(pk=self.get_user(self.user1).id)
        self.assertTrue(highscore.score == 2)

    def test_get_highscore(self):
        self.register(self.user1)
        self.get_token(self.user1)
        self.submit_match(1)
        response = self.client.get('/user/highscore/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 1)
        self.assertEqual(response.data['rank'], 1)

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
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['pages'], 1)

    def test_highscores_pages(self):
        self.register(self.user1)
        self.get_token(self.user1)
        self.submit_match(1)
        self.register(self.user2)
        self.get_token(self.user2)
        self.submit_match(2)

        # logout
        self.client.credentials()

        response = self.client.get('/highscores/0/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        e = response.data[0]
        self.assertEqual(e['player_name'], 'test-user-2')
        self.assertEqual(e['score'], 2)

        e = response.data[1]
        self.assertEqual(e['player_name'], 'test-user-1')
        self.assertEqual(e['score'], 1)

class MatchSubmissionHighscoreTest(UserAPITestCase):
    """Testing the submission of matches and the highscore
        update algorithm"""

    def submit_match(self):
        data = {'score': 123456}
        response = self.client.post('/user/matches/', data)
        return response

    def test_submit_match_with_login(self):
        """ Submit match data """
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert match object creation
        matches = Match.objects.filter(player=self.get_user(self.user1))
        self.assertTrue(matches[0].score == 123456)

    def test_submit_match_creation(self):
        """ Submit match data """
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert match object creation
        matches = Match.objects.filter(player=self.get_user(self.user1))
        self.assertTrue(matches[0].score == 123456)

    def test_submit_highscore_update(self):
        """ Submit match data """
        self.register(self.user1)
        self.get_token(self.user1)
        response = self.submit_match()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert highscore update
        highscore = Highscore.objects.get(pk=self.get_user(self.user1).id)
        self.assertTrue(highscore.score == 123456)

    def test_submit_match_without_login(self):
        response = self.submit_match()
        self.assertEqual(response.status_code, 401)

