from werkzeug.security import generate_password_hash
from app import db
from flask import request, jsonify
from ..models.history import History, History_schema, Historys_schema
from openai import OpenAI
import json
import os
import PyPDF2

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
        description = result['description'].replace("'", '"')
        description = json.loads(description)
        return json.dumps(description, indent=4)

    return jsonify({'message': "history don't exist", 'data': {}}), 404

def get_chat_chumbado(current_user):
    history = History.query.filter_by(user_id=current_user.id).order_by(History.id.desc()).first()
    if history:
        result = History_schema.dump(history)
        description = result['description'].replace("'", '"')
        description = json.loads(description)
        return json.dumps(description, indent=4)

def validate_json(response_content):

    try:
        data = json.loads(response_content)
        return data
    
    except json.JSONDecodeError:
        return None

def get_gpt(current_user):

    cargo = request.json.get('cargo', '')
    tecnologia = request.json.get('tecnologia', '')
    tempoMaximoNumero = request.json.get('tempoMaximoNumero', '')
    tempoMaximoTipo = request.json.get('tempoMaximoTipo', '')
    tempoMedioNumero = request.json.get('tempoMedioNumero', '')
    tempoMedioTipo = request.json.get('tempoMedioTipo', '')
    formatoEstudos = request.json.get('formatoEstudos', '')
    dadosPdf = upload_and_read_pdf()

    prompt = f"""
    Eu preciso de algumas etapas para chegar ao cargo de {cargo}, na tecnologia: {tecnologia}.
    O tempo total de estudos deve ser no máximo: {tempoMaximoNumero} {tempoMaximoTipo}, considerando um tempo médio semanal de {tempoMedioNumero} {tempoMedioTipo}. 
    O formato de didática preferido é: {formatoEstudos}. 
    """

    if dadosPdf:
        contato = "Contato: "+dadosPdf.contato+"\n"
        competencia = "Principais competências: "+dadosPdf.competencia+"\n"
        resumo = "Resumo: "+dadosPdf.resumo+"\n"
        experiencia = "Experiência: "+dadosPdf.experiencia+"\n"
        formacao = "Formação acadêmica: "+dadosPdf.formacao+"\n"
        prompt += f"""
        Considere que o usuário possui as seguintes informações adicionais:
        {contato} {competencia} {resumo} {experiencia} {formacao}
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
        if completion and hasattr(completion, 'choices'):
            content = completion.choices[0].message.content
            validated_data = validate_json(content)
            if validated_data:
                # Salvar no banco de dados historico
                title = "Chat dia hoje"
                history = History(title=title, description=validated_data, user_id=current_user.id)
                db.session.add(history)
                db.session.commit()
                return validated_data

    return jsonify({'message': 'error on generate completion'}), 500
    
    

contato = "\nContato\n"
competencia="\nPrincipais competências\n"
resumo = "\nResumo\n"
experiencia="\nExperiência\n"
formacao="\nFormação acadêmica\n"


UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


#Função para fazer upload de PDF e ler seu conteúdo.

def upload_and_read_pdf():
    if 'pdf' not in request.files:
        return False

    # Recebendo o arquivo do front do tipo multipart/form-data e acessando com o dicionário
    pdf_file = request.files['pdf']

    if pdf_file.filename == '':
        return {'error': 'Nome de arquivo inválido'}

    if pdf_file and pdf_file.filename.endswith('.pdf'):
      
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        pdf_file.save(pdf_path)

        texto_completo = ""
        cont=""
        comp=""
        resu=""
        expe=""
        form=""
        #Ler o conteúdo do PDF
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    texto_completo += page.extract_text()
                
                cont=intervalo(texto_completo,contato,competencia)
                comp=intervalo(texto_completo,competencia,resumo)
                resu=intervalo(texto_completo,resumo,experiencia)
                expe=intervalo(texto_completo,experiencia,formacao)
                form=intervalo(texto_completo,formacao,formacao)

            return {'contato':cont,'competencia':comp,'resumo':resu,'experiencia':expe,'formacao':form}
        except Exception as e:
            return {'error': 'Erro ao processar o PDF', 'details': str(e)}
    else:
        return {'error': 'Apenas arquivos PDF são permitidos!'}

#Função para separar cada campo do PDF
def intervalo(texto, palavra_inicio, palavra_fim):
    
    partes = texto.split(palavra_inicio)
    
    
    if len(partes) > 1:
        intervalo_texto = partes[1].split(palavra_fim)[0]
        return intervalo_texto.strip()  
    else:
        return "Palavras de início ou fim não encontradas no texto."
