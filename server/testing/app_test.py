import flask
import pytest

from app import app
from models import db, User

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'


class TestApp:
    '''Flask API in app.py'''

    def setup_method(self):
        """Runs before each test"""
        with app.app_context():
            db.drop_all()
            db.create_all()

    def test_creates_users_at_signup(self):
        '''creates user records with usernames and passwords at /signup.'''

        with app.test_client() as client:
            response = client.post('/signup', json={
                'username': 'ash',
                'password': 'pikachu',
            })

            assert response.status_code == 201
            assert response.get_json()['username'] == 'ash'

            with app.app_context():
                assert User.query.filter_by(username='ash').first()

    def test_logs_in(self):
        '''logs users in with a username and password at /login.'''

        with app.test_client() as client:
            client.post('/signup', json={
                'username': 'ash',
                'password': 'pikachu',
            })

            response = client.post('/login', json={
                'username': 'ash',
                'password': 'pikachu',
            })

            assert response.get_json()['username'] == 'ash'

            with client.session_transaction() as session:
                user = User.query.filter_by(username='ash').first()
                assert session.get('user_id') == user.id

    def test_logs_out(self):
        '''logs users out at /logout.'''

        with app.test_client() as client:
            client.post('/signup', json={
                'username': 'ash',
                'password': 'pikachu',
            })

            client.post('/login', json={
                'username': 'ash',
                'password': 'pikachu',
            })

            # confirm logged in
            with client.session_transaction() as session:
                assert session.get('user_id')

            # logout
            response = client.delete('/logout')
            assert response.status_code == 204

            with client.session_transaction() as session:
                assert not session.get('user_id')

    def test_checks_for_session(self):
        '''checks if a user is authenticated and returns the user as JSON at /check_session.'''

        with app.test_client() as client:
            client.post('/signup', json={
                'username': 'ash',
                'password': 'pikachu',
            })

            client.post('/login', json={
                'username': 'ash',
                'password': 'pikachu',
            })

            response = client.get('/check_session')
            assert response.get_json()['username'] == 'ash'

            client.delete('/logout')

            response = client.get('/check_session')
            assert response.status_code == 204
            assert not response.data
