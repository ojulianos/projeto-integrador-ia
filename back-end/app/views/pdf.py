"""
import os
from flask import request, jsonify
import PyPDF2
from app import app

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

        #Ler o conteúdo do PDF

        texto_completo = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    texto_completo += page.extract_text()

            return jsonify({'message': 'PDF enviado e lido com sucesso!', 'content': texto_completo}), 200
        except Exception as e:
            return jsonify({'error': 'Erro ao processar o PDF', 'details': str(e)}), 500
    else:
        return jsonify({'error': 'Apenas arquivos PDF são permitidos!'}), 400
"""