#!/usr/bin/env python3
"""
Organizador de Processo - API Flask Orquestrador
Coordena os módulos para processar documentos
"""
import os
import logging
from flask import Flask, render_template, request, jsonify
from modulos.config import UPLOAD_FOLDER, LOG_FILE, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from modulos.arquivo import processar_upload
from modulos.processador import (
    processar_lista_inputs, 
    processar_upload_com_organizacao,
    extrair_numero_do_filename
)

# Criar app Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ ROTAS ============

@app.route('/')
def index():
    """Página principal"""
    logger.info("Acesso à página principal")
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_arquivo():
    """
    Endpoint de upload de arquivo
    Salva arquivo e processa com lógica de movimentação e organização
    """
    try:
        logger.info("Recebimento de requisição de upload")
        
        if 'arquivo' not in request.files:
            return jsonify({
                "status": "erro",
                "mensagem": "Nenhum arquivo foi enviado"
            }), 400
        
        arquivo = request.files['arquivo']
        numero_processo = request.form.get('numero_processo', '').strip()
        caminho_processo = request.form.get('caminho_processo', '').strip()
        
        # Processar upload básico (salva temporariamente)
        resultado = processar_upload(arquivo, numero_processo, caminho_processo)
        
        if resultado['status'] != 'sucesso':
            logger.warning(f"Erro no upload: {resultado['mensagem']}")
            return jsonify(resultado), 400
        
        # Se temos número de processo, processar com organização
        if numero_processo:
            arquivo_path = resultado['arquivo']['caminho']
            resultado_com_org = processar_upload_com_organizacao(arquivo_path, numero_processo)
            
            logger.info(f"Upload processado com organização: {numero_processo}")
            return jsonify(resultado_com_org), 200
        
        # Caso contrário, apenas retornar resultado do upload
        logger.info(f"Upload bem-sucedido: {arquivo.filename}")
        return jsonify(resultado), 200
    
    except Exception as e:
        logger.error(f"Exceção no upload: {str(e)}", exc_info=True)
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao fazer upload: {str(e)}"
        }), 500


@app.route('/api/processar', methods=['POST'])
def processar():
    """
    Endpoint para processar caminhos
    """
    try:
        logger.info("Recebimento de requisição de processamento")
        
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                "status": "erro",
                "mensagem": "Nenhum dado foi enviado"
            }), 400
        
        inputs = dados.get('inputs', [])
        logger.info(f"Processando {len(inputs)} input(s)")
        
        # Processar
        resultado = processar_lista_inputs(inputs)
        
        if resultado['status'] in ['sucesso', 'sucesso_parcial']:
            logger.info(f"Processamento concluído: {resultado.get('resumo', {})}")
            return jsonify(resultado), 200
        else:
            logger.warning(f"Erro no processamento: {resultado.get('mensagem')}")
            return jsonify(resultado), 400
    
    except Exception as e:
        logger.error(f"Exceção no processamento: {str(e)}", exc_info=True)
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao processar: {str(e)}"
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """
    Endpoint de status da aplicação
    """
    from datetime import datetime
    from modulos.config import DIRETORIO_BASE
    
    logger.info("Verificação de status")
    
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "diretorio_base": DIRETORIO_BASE,
        "pasta_uploads": UPLOAD_FOLDER,
        "extensoes_permitidas": list(ALLOWED_EXTENSIONS),
        "tamanho_maximo_mb": MAX_FILE_SIZE / (1024 * 1024)
    }), 200


# ============ TRATAMENTO DE ERROS ============

@app.errorhandler(413)
def arquivo_muito_grande(error):
    """Tratamento para arquivo muito grande"""
    logger.error("Arquivo muito grande enviado")
    return jsonify({
        "status": "erro",
        "mensagem": f"Arquivo muito grande. Máximo permitido: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
    }), 413


@app.errorhandler(500)
def erro_interno(error):
    """Tratamento para erro interno"""
    logger.error(f"Erro interno: {str(error)}", exc_info=True)
    return jsonify({
        "status": "erro",
        "mensagem": "Erro interno do servidor"
    }), 500


# ============ INICIALIZAÇÃO ============

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Iniciando Organizador de Processo - API Flask")
    logger.info(f"Pasta de uploads: {UPLOAD_FOLDER}")
    logger.info(f"Log: {LOG_FILE}")
    logger.info("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )