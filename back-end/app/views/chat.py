from werkzeug.security import generate_password_hash
from app import db
from flask import request, jsonify
from ..models.history import History, History_schema, Historys_schema
import openai

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

    cargo = request.json.get('cargo', '')
    tecnologia = request.json.get('tecnologia', '')
    tempoMaximo = request.json.get('tempoMaximo', '')
    tempoMedio = request.json.get('tempoMedio', '')
    formatoEstudos = request.json.get('formatoEstudos', '')

    prompt = f"""
    Eu preciso saber quais as etapas para chegar ao cargo de {cargo}, na tecnologia {tecnologia},gostaria que me adequasse para que leve no máximo de {tempoMaximo},
    sendo que possuo um tempo médio semanal de {tempoMedio}, preciso que me indique principalmente o formato de didádica {formatoEstudos}.
    """

    openai.api_key=""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
            "role": "system",
            "content": """
                Você é um assistente que vai dar respostas diretas, relacionadas a o que a pessoa deve estudar para alcançar seus obejtivos.
                Preciso que você sugira livros, sites de acordo com a didatica escolhida pelo usuário, e o tempo total que o usuário deseja, 
                será informado no prompt, mas você ficará com a responsabilidade de separar o tempo de cada etapa para se tornar apto.
                O usuário também terá a possibilidade de importar um pdf, onde será lhe passado no prompt, as informações contidas, preciso que analise 
                o currículo e capte as experiências que o usuário já possui, tornando sua resposta mais acertiva, busque sempre procurar opções de indicação gratuitas
                Sempre responda ao usuário no seguinte formato de Json. 
            """
        },
            {
            "role" : "user",
            "content" : prompt
        }
        ],
        temperature=0.5,
        max_tokens=2048,
        top_p=0.9,
        frequency_penalty=1,
        presence_penalty=1,
    )
    return response.choices[0].message.content

