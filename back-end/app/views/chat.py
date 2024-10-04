from werkzeug.security import generate_password_hash
from app import db
from flask import request, jsonify
from ..models.history import History, History_schema, Historys_schema
from openai import OpenAI

"""Retorna detalhes do chatGPT e histórico"""
def get_chats(user_id = ""):
    texto = request.args.get('texto')
    if texto:
        history = History.query.filter(History.description.like(f'%{texto}%')).all()
    else:
        history = History.query.all()
    if history:
        result = History_schema.dump(user_id)
        return jsonify({'message': 'successfully fetched', 'data': result.data})

    return jsonify({'message': 'nothing found', 'data': {}})

"""Retorna usuário específico pelo ID no parametro da request"""
def get_chat(id):
    history = History.query.get(id)
    if history:
        result = History_schema.dump(history)
        return jsonify({'message': 'successfully fetched', 'data': result.data}), 201

    return jsonify({'message': "history don't exist", 'data': {}}), 404

def get_gpt():
    textoGPT = request.args.get('texto')

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": textoGPT
                    }
                ]
            }
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json"
        }
    )
    return jsonify(response)

