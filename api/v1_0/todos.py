from flask import request
from ..models import db, Todo
from ..decorators import json, paginate, etag, rate_limit, hit_count
from ..auth import auth
from . import api


@api.route('/todos/', methods=['GET'])
@rate_limit(limit=45, per=15)
@auth.login_required
@etag
@paginate()
def get_todos():
  return Todo.query


@api.route('/todos/<int:id>', methods=['GET'])
@rate_limit(limit=5, per=15)
@hit_count
@etag
@json
def get_todo(id):
  return Todo.query.get_or_404(id)


@api.route('/todos/', methods=['POST'])
@auth.login_required
@json
def new_todo():
  todo = Todo().from_json(request.json)
  db.session.add(todo)
  db.session.commit()
  return {}, 201, {'Location': todo.get_url()}


@api.route('/todos/<int:id>', methods=['PUT'])
@auth.login_required
@json
def edit_todo(id):
  todo = Todo.query.get_or_404(id)
  todo.from_json(request.json)
  db.session.add(todo)
  db.session.commit()
  return {}


@api.route('/todos/<int:id>', methods=['DELETE'])
@auth.login_required
@json
def delete_todo(id):
  todo = Todo.query.get_or_404(id)
  db.session.delete(todo)
  db.session.commit()
  return {}
