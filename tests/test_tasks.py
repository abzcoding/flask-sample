import unittest
from werkzeug.exceptions import BadRequest
from .test_client import TestClient
from api.app import create_app
from api.models import db
from api.errors import ValidationError
from api.helpers import convert_url
from api.tasks import sample
import time


class TestTasks(unittest.TestCase):
  default_username = 'mamad'
  default_password = 'jafar'

  def setUp(self):
    self.app = create_app('test_config')
    self.ctx = self.app.app_context()
    self.ctx.push()
    db.drop_all()
    db.create_all()
    self.client = TestClient(self.app, None, None)
    self.task = sample.apply()
    self.results = self.task.get()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.ctx.pop()

  def test_sample(self):
    self.assertEqual(self.task.state, "SUCCESS")
