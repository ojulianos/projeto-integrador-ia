
import os
from flask import request, jsonify
import PyPDF2
from app import app


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
        return jsonify({'error': 'Nenhum arquivo PDF enviado'}), 400

    # Recebendo o arquivo do front do tipo multipart/form-data e acessando com o dicionário
    pdf_file = request.files['pdf']

    if pdf_file.filename == '':
        return jsonify({'error': 'Nome de arquivo inválido'}), 400

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

            return jsonify({'message': 'PDF enviado e lido com sucesso!', 'content':{'contato':cont,'competencia':comp,'resumo':resu,'experiencia':expe,'formacao':form} }), 200
        except Exception as e:
            return jsonify({'error': 'Erro ao processar o PDF', 'details': str(e)}), 500
    else:
        return jsonify({'error': 'Apenas arquivos PDF são permitidos!'}), 400

#Função para separar cada campo do PDF
def intervalo(texto, palavra_inicio, palavra_fim):
    
    partes = texto.split(palavra_inicio)
    
    
    if len(partes) > 1:
        intervalo_texto = partes[1].split(palavra_fim)[0]
        return intervalo_texto.strip()  
    else:
        return "Palavras de início ou fim não encontradas no texto."
