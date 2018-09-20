import unittest
from werkzeug.exceptions import BadRequest
from .test_client import TestClient
from api.app import create_app
from api.models import db, User
from api.errors import ValidationError
from api.helpers import convert_url


class TestTokenAPI(unittest.TestCase):
  default_username = 'mamad'
  default_password = 'jafar'

  def setUp(self):
    self.app = create_app('test_config')
    self.ctx = self.app.app_context()
    self.ctx.push()
    db.drop_all()
    db.create_all()
    u = User(username=self.default_username, password=self.default_password)
    db.session.add(u)
    db.session.commit()
    self.client = TestClient(self.app, u.generate_auth_token(), '')

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.ctx.pop()

  def test_password_auth(self):
    self.app.config['USE_TOKEN_AUTH'] = False
    good_client = TestClient(self.app, self.default_username,
                             self.default_password)
    rv, _ = good_client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 200)

    self.app.config['USE_TOKEN_AUTH'] = True
    u = User.query.get(1)
    good_client = TestClient(self.app, u.generate_auth_token(), '')
    rv, json = good_client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 200)

  def test_bad_auth(self):
    bad_client = TestClient(self.app, 'abc', 'def')
    rv, _ = bad_client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 401)

    self.app.config['USE_TOKEN_AUTH'] = True
    bad_client = TestClient(self.app, 'bad_token', '')
    rv, json = bad_client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 401)

  def test_rate_limits(self):
    self.app.config['USE_RATE_LIMITS'] = True

    rv, _ = self.client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 200)
    self.assertTrue('X-RateLimit-Remaining' in rv.headers)
    self.assertTrue('X-RateLimit-Limit' in rv.headers)
    self.assertTrue('X-RateLimit-Reset' in rv.headers)
    self.assertTrue(
        int(rv.headers['X-RateLimit-Limit']) ==
        int(rv.headers['X-RateLimit-Remaining']) + 1)
    while int(rv.headers['X-RateLimit-Remaining']) > 0:
      rv, json = self.client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 429)

  def test_pagination(self):
    # create several students
    rv, json = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'one',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 201)
    one_url = rv.headers['Location']
    rv, json = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'two',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 201)
    two_url = rv.headers['Location']
    rv, json = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'three',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 201)
    three_url = rv.headers['Location']
    rv, json = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'four',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 201)
    four_url = rv.headers['Location']
    rv, json = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'five',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 201)
    five_url = rv.headers['Location']

    # get collection in pages
    rv, json = self.client.get('/api/v1.0/todos/?page=1&per_page=2')
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(one_url in json['urls'])
    self.assertTrue(two_url in json['urls'])
    self.assertTrue(len(json['urls']) == 2)
    self.assertTrue('total' in json['meta'])
    self.assertTrue(json['meta']['total'] == 5)
    self.assertTrue('prev' in json['meta'])
    self.assertTrue(json['meta']['prev'] is None)
    first_url = json['meta']['first'].replace('http://localhost', '')
    last_url = json['meta']['last'].replace('http://localhost', '')
    next_url = json['meta']['next'].replace('http://localhost', '')

    rv, json = self.client.get(first_url)
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(one_url in json['urls'])
    self.assertTrue(two_url in json['urls'])
    self.assertTrue(len(json['urls']) == 2)

    rv, json = self.client.get(next_url)
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(three_url in json['urls'])
    self.assertTrue(four_url in json['urls'])
    self.assertTrue(len(json['urls']) == 2)
    next_url = json['meta']['next'].replace('http://localhost', '')

    rv, json = self.client.get(next_url)
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(five_url in json['urls'])
    self.assertTrue(len(json['urls']) == 1)

    rv, json = self.client.get(last_url)
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(five_url in json['urls'])
    self.assertTrue(len(json['urls']) == 1)

  def test_cache_control(self):
    client = TestClient(self.app, self.default_username, self.default_password)
    rv, json = client.get('/auth/request-token')
    self.assertTrue(rv.status_code == 200)
    self.assertTrue('Cache-Control' in rv.headers)
    cache = [c.strip() for c in rv.headers['Cache-Control'].split(',')]
    self.assertTrue('no-cache' in cache)
    self.assertTrue('no-store' in cache)
    self.assertTrue('max-age=0' in cache)
    self.assertTrue(len(cache) == 3)

  def test_etag(self):
    # create two todos
    rv, _ = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'one',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 201)
    one_url = rv.headers['Location']
    rv, json = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'two',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 201)
    two_url = rv.headers['Location']

    # get their etags
    rv, json = self.client.get(one_url)
    self.assertTrue(rv.status_code == 200)
    one_etag = rv.headers['ETag']
    rv, json = self.client.get(two_url)
    self.assertTrue(rv.status_code == 200)
    two_etag = rv.headers['ETag']

    # send If-None-Match header
    rv, json = self.client.get(one_url, headers={'If-None-Match': one_etag})
    self.assertTrue(rv.status_code == 304)
    rv, json = self.client.get(
        one_url, headers={'If-None-Match': one_etag + ', ' + two_etag})
    self.assertTrue(rv.status_code == 304)
    rv, json = self.client.get(one_url, headers={'If-None-Match': two_etag})
    self.assertTrue(rv.status_code == 200)
    rv, json = self.client.get(
        one_url, headers={'If-None-Match': two_etag + ', *'})
    self.assertTrue(rv.status_code == 304)

    # send If-Match header
    rv, json = self.client.get(one_url, headers={'If-Match': one_etag})
    self.assertTrue(rv.status_code == 200)
    rv, json = self.client.get(
        one_url, headers={'If-Match': one_etag + ', ' + two_etag})
    self.assertTrue(rv.status_code == 200)
    rv, json = self.client.get(one_url, headers={'If-Match': two_etag})
    self.assertTrue(rv.status_code == 412)
    rv, json = self.client.get(one_url, headers={'If-Match': '*'})
    self.assertTrue(rv.status_code == 200)

    # change a resource
    rv, json = self.client.put(
        one_url, data={
            'name': 'not-one',
            'task': 'sth'
        })
    self.assertTrue(rv.status_code == 200)

    # use stale etag
    rv, json = self.client.get(one_url, headers={'If-None-Match': one_etag})
    self.assertTrue(rv.status_code == 200)

  def test_helpers(self):
    self.assertEqual(convert_url('www.google.com'), 'http://www.google.com')
    with self.assertRaises(ValidationError):
      convert_url('bad url')

  def test_todos(self):
    # get collection
    rv, json = self.client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(json['urls'] == [])

    # create new
    rv, json = self.client.post(
        '/api/v1.0/todos/', data={
            'name': 'buy',
            'task': 'buy groceries'
        })
    self.assertTrue(rv.status_code == 201)
    buy_url = rv.headers['Location']

    # get
    rv, json = self.client.get(buy_url)
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(json['name'] == 'buy')
    self.assertTrue(json['url'] == buy_url)

    # create new
    rv, json = self.client.post(
        '/api/v1.0/todos/',
        data={
            'name': 'clean',
            'task': 'clean dining room'
        })
    self.assertTrue(rv.status_code == 201)
    clean_url = rv.headers['Location']

    # get
    rv, json = self.client.get(clean_url)
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(json['name'] == 'clean')
    self.assertTrue(json['url'] == clean_url)

    # create bad request
    rv, json = self.client.post('/api/v1.0/todos/', data={})
    self.assertTrue(rv.status_code == 400)

    self.assertRaises(ValidationError, lambda:
                      self.client.post('/api/v1.0/todos/',
                                       data={'not-name': 'clean'}))

    # modify
    rv, json = self.client.put(
        clean_url, data={
            'name': 'clean',
            'task': 'clean bathroom'
        })
    self.assertTrue(rv.status_code == 200)

    # get
    rv, json = self.client.get(clean_url)
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(json['task'] == 'clean bathroom')

    # get collection
    rv, json = self.client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 200)
    self.assertTrue(buy_url in json['urls'])
    self.assertTrue(clean_url in json['urls'])
    self.assertTrue(len(json['urls']) == 2)

    # delete
    rv, json = self.client.delete(buy_url)
    self.assertTrue(rv.status_code == 200)

    # get collection
    rv, json = self.client.get('/api/v1.0/todos/')
    self.assertTrue(rv.status_code == 200)
    self.assertFalse(buy_url in json['urls'])
    self.assertTrue(clean_url in json['urls'])
    self.assertTrue(len(json['urls']) == 1)
