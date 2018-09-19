from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from .errors import ValidationError

db = SQLAlchemy()


class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), index=True)
  task = db.Column(db.String(250))
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)

  def get_url(self):
    return url_for('api.get_todo', id=self.id, _external=True)

  def to_json(self):
    return {
      'url': self.get_url(),
      'name': self.name,
      'task': self.task,
      'timestamp': self.timestamp
    }

  def from_json(self, json):
    try:
      self.name = json['name']
      self.task = json['task']
    except KeyError as e:
      raise ValidationError('Invalid todo: missing ' + e.args[0])
    return self


class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True)
  password_hash = db.Column(db.String(128))

  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

  def generate_auth_token(self, expires_in=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
    return s.dumps({'id': self.id}).decode('utf-8')

  @staticmethod
  def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
      data = s.loads(token)
    except Exception:
      return None
    return User.query.get(data['id'])

