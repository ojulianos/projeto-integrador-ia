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

def get_gpt():

    try:
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
            api_key="",
        )
        
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                "role": "system",
                "content": """
                    Você é um assistente que vai dar respostas diretas, relacionadas a o que a pessoa deve estudar para alcançar seus objetivos.
                    Preciso que você sugira livros, sites de acordo com a didática escolhida pelo usuário, e o tempo total que o usuário deseja, 
                    de acordo com o informado pelo mesmo, mas você ficará com a responsabilidade de separar o tempo de cada etapa para se tornar apto.
                    O usuário também terá a possibilidade de importar um pdf, onde será lhe passado no prompt, as informações contidas, preciso que analise 
                    o currículo e capte as experiências que o usuário já possui, tornando sua resposta mais acertiva, busque sempre procurar opções de indicação gratuitas
                    Sempre responda ao usuário no seguinte formato de Json seguindo o modelo abaixo:
                    {
                        "Etapas": [
                            {
                                "Etapa": "Nome da Etapa",
                                "Recursos": [
                                    {
                                        "Tipo": "Livro",
                                        "Título": "Título do Livro",
                                        "Link": "Link para compra/acesso"
                                    },
                                    {
                                        "Tipo": "Curso online",
                                        "Nome": "Nome do Curso",
                                        "Link": "Link para acesso"
                                    }
                                ],
                                "TempoEstudoSemanal": "Duração em horas",
                                "DuracaoTotal": "Duração total da etapa em meses"
                            }
                        ]
                    }

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
        )

        return jsonify({'message': 'successfully fetched', 'data': completion.choices[0].message.content}), 200
    except:
        return jsonify({'message': 'unable to fetch', 'data': {}}), 500
    

