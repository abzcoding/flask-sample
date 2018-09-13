from flask import request
from ..models import db, Todo
from ..decorators import json, paginate, etag
from . import api


@api.route('/todos/', methods=['GET'])
@etag
@paginate()
def get_todos():
    return Todo.query


@api.route('/todos/<int:id>', methods=['GET'])
@etag
@json
def get_todo(id):
    return Todo.query.get_or_404(id)


@api.route('/todos/', methods=['POST'])
@json
def new_todo():
    todo = Todo().from_json(request.json)
    db.session.add(todo)
    db.session.commit()
    return {}, 201, {'Location': todo.get_url()}


@api.route('/todos/<int:id>', methods=['PUT'])
@json
def edit_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.from_json(request.json)
    db.session.add(todo)
    db.session.commit()
    return {}


@api.route('/todos/<int:id>', methods=['DELETE'])
@json
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return {}
