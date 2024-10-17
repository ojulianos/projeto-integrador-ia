from app import app
from flask import jsonify, url_for, redirect
from ..views import users, chat, helper

"""Neste arquivo iremos criar todas rotas para aplicação para manter o código limpo usando
 as views(controllers)  e as relacionando por meio de funções"""


@app.route('/v1', methods=['GET'])
@helper.token_required
def root(current_user):
    return jsonify({'message': f'Hello {current_user.name}'})


@app.route('/v1/authenticate', methods=['POST'])
def authenticate():
    return helper.auth()


@app.route('/v1/users', methods=['GET'])
def get_users():
    return users.get_users()


@app.route('/v1/users/<id>', methods=['GET'])
def get_user(id):
    return users.get_user(id)


@app.route('/v1/users', methods=['POST'])
def post_users():
    return users.post_user()


@app.route('/v1/users/<id>', methods=['DELETE'])
def delete_users(id):
    return users.delete_user(id)


@app.route('/v1/users/<id>', methods=['PUT'])
def update_users(id):
    return users.update_user(id)

@app.route('/v1/history/<user_id>/user', methods=['GET'])
def get_chats(user_id):
    return chat.get_chats(user_id)

@app.route('/v1/history/<id>', methods=['GET'])
def get_chat(id):
    return chat.get_chat(id)

@app.route('/v1/chat', methods=['POST'])
def get_gpt():
    return chat.get_gpt()

@app.route('/v1/chat_chumbado', methods=['POST'])
def get_gpt_chumbado():
    return chat.get_chat_chumbado()

@app.route('/v1/auth', methods=['POST'])
def auth():
    pass

