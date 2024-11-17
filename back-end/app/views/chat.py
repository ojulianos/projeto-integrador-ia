from werkzeug.security import generate_password_hash
from app import db
from flask import request, jsonify
from ..models.history import History, History_schema, Historys_schema
from openai import OpenAI
import json

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

def get_chat_chumbado():
    json = """
        {
        "Etapas": [
            {
                "Etapa": "Aprofundamento em fundamentos PHP",
                "Recursos": [
                    {
                        "Tipo": "Livro",
                        "Título": "PHP & MySQL: Server-side Web Development",
                        "Link": "https://www.amazon.com/PHP-MySQL-Server-side-Development-Learn/dp/1119149223"
                    },
                    {
                        "Tipo": "Curso online",
                        "Nome": "Learn PHP - Codecademy",
                        "Link": "https://www.codecademy.com/learn/learn-php"
                    }
                ],
                "TempoEstudoSemanal": "2 horas",
                "DuracaoTotal": "6 meses"
            },
            {
                "Etapa": "Aprofundamento em programação orientada a objetos com PHP",
                "Recursos": [
                    {
                        "Tipo": "Livro",
                        "Título": "Mastering Object-oriented PHP",
                        "Link": "https://www.amazon.com/Mastering-Object-Oriented-PHP-Jordan-Tamayo/dp/B01K3I9Y4O"
                    },
                    {
                        "Tipo": "Curso online",
                        "Nome": "Object Oriented PHP & MVC - Udemy",
                        "Link": "https://www.udemy.com/course/object-oriented-php-mvc/"
                    }
                ],
                "TempoEstudoSemanal": "2 horas",
                "DuracaoTotal": "6 meses"
            }
        ]
    }
    """
    return json

def validate_json(response_content):

    try:
        data = json.loads(response_content)
        return data
    
    except json.JSONDecodeError:
        return None

def get_gpt():

    cargo = request.json.get('cargo', '')
    tecnologia = request.json.get('tecnologia', '')
    tempoMaximo = request.json.get('tempoMaximo', '')
    tempoMedio = request.json.get('tempoMedio', '')
    formatoEstudos = request.json.get('formatoEstudos', '')

    prompt = f"""
    Eu preciso de algumas etapas para chegar ao cargo de {cargo}, na tecnologia: {tecnologia}.
    O tempo total de estudos deve ser no máximo: {tempoMaximo}, considerando um tempo médio semanal de {tempoMedio}. 
    O formato de didática preferido é: {formatoEstudos}. 
    """

    client = OpenAI(
        api_key=""
    )

    def generate_completion():
        try:
            return client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
                            Você é um assistente que vai dar respostas diretas, relacionadas a o que a pessoa deve estudar para alcançar seus objetivos.
                            Preciso que você sugira livros, sites de acordo com a didática escolhida pelo usuário, e o tempo total que o usuário deseja, 
                            de acordo com o informado pelo mesmo, mas você ficará com a responsabilidade de separar o tempo de cada etapa para se tornar apto.
                            O usuário também terá a possibilidade de importar um pdf, onde será lhe passado no prompt, as informações contidas, preciso que analise 
                            o currículo e capte as experiências que o usuário já possui, tornando sua resposta mais acertiva, busque sempre procurar opções de indicação gratuitas

                        Se atente ao formato Json, precisa retornar da forma mais estruturada possível, qualquer erro na formatação, acabará impactando na
                        performace da solução.
                        """
                    },
                    {
                        "role" : "user",
                        "content" : prompt
                    }
                ],
                temperature=0.5,
                top_p=0.9,
                frequency_penalty=1,
                presence_penalty=1,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "email_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "etapas": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "etapa": {
                                                "description": "nome da etapa",
                                                "type": "string"
                                            },
                                            "recursos": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "tipo": {
                                                            "description": "tipo de recurso",
                                                            "type": "string"
                                                        },
                                                        "titulo": {
                                                            "description": "título do recurso",
                                                            "type": "string"
                                                        },
                                                        "link": {
                                                            "description": "link do recurso",
                                                            "type": "string"
                                                        }
                                                    }
                                                }
                                            },
                                            "tempoEstudoSemanal": {
                                                "description": "Duração em horas",
                                                "type": "string"
                                            },
                                            "duracaoTotal": {
                                                "description": "Duração total da etapa em meses",
                                                "type": "string"
                                            }
                                        }
                                    }
                                },
                                "additionalProperties": False
                            }
                        }
                    }
                }
            )
        except Exception as e:
            print(f"Erro ao chamar a API: {e}")
            return None
        
    for _ in range(3):  
        completion = generate_completion()
        if completion and "choices" in completion:
            content = completion.choices[0].message.content
            validated_data = validate_json(content)
            if validated_data: 
                return validated_data

    return completion.choices[0].message.content
    

