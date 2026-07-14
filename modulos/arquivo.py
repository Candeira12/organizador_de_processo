"""
Lógica para gerenciamento de uploads de arquivo
"""
import os
import logging
from werkzeug.utils import secure_filename
from modulos.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from modulos.utils import gerar_nome_arquivo, formatar_tamanho_arquivo, validar_numero_processo

logger = logging.getLogger(__name__)


def validar_arquivo(arquivo):
    """
    Valida se um arquivo pode ser enviado
    """
    if not arquivo:
        return False, "Nenhum arquivo foi fornecido"
    
    if arquivo.filename == '':
        return False, "Nenhum arquivo foi selecionado"
    
    if not tem_extensao_permitida(arquivo.filename):
        extensoes = ', '.join(ALLOWED_EXTENSIONS)
        return False, f"Tipo de arquivo não permitido. Permitidos: {extensoes}"
    
    return True, "Arquivo válido"


def tem_extensao_permitida(filename):
    """
    Verifica se o arquivo tem extensão permitida
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validar_processo_input(numero_processo, caminho_processo):
    """
    Valida se pelo menos um tipo de identificação foi fornecido
    """
    numero_processo = numero_processo.strip()
    caminho_processo = caminho_processo.strip()
    
    if not numero_processo and not caminho_processo:
        return False, "É necessário fornecer número do processo OU caminho completo"
    
    if numero_processo and not validar_numero_processo(numero_processo):
        return False, "Formato de número de processo inválido. Use: xxxxxxx-xx.xxxx.x.xx.xxxx"
    
    return True, "Entrada válida"


def salvar_arquivo_upload(arquivo):
    """
    Salva o arquivo enviado temporariamente e retorna informações
    """
    try:
        filename = secure_filename(arquivo.filename)
        filename_salvo = gerar_nome_arquivo(arquivo.filename)
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, filename_salvo)
        
        arquivo.save(caminho_arquivo)
        tamanho = os.path.getsize(caminho_arquivo)
        
        logger.info(f"Arquivo salvo temporariamente: {caminho_arquivo}")
        
        return True, {
            "nome_original": arquivo.filename,
            "nome_salvo": filename_salvo,
            "caminho": caminho_arquivo,
            "tamanho": tamanho,
            "tamanho_formatado": formatar_tamanho_arquivo(tamanho)
        }
    
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo: {str(e)}")
        return False, {
            "erro": str(e)
        }


def processar_upload(arquivo, numero_processo, caminho_processo):
    """
    Processa um upload - salva temporariamente
    A lógica de movimentação e execução do organizador está em processador.py
    """
    # Validar arquivo
    valido, mensagem = validar_arquivo(arquivo)
    if not valido:
        return {
            "status": "erro",
            "mensagem": mensagem
        }
    
    # Validar entrada de processo
    valido, mensagem = validar_processo_input(numero_processo, caminho_processo)
    if not valido:
        return {
            "status": "erro",
            "mensagem": mensagem
        }
    
    # Salvar arquivo
    sucesso, info = salvar_arquivo_upload(arquivo)
    if not sucesso:
        return {
            "status": "erro",
            "mensagem": f"Erro ao salvar arquivo: {info['erro']}"
        }
    
    return {
        "status": "sucesso",
        "mensagem": "Arquivo enviado com sucesso",
        "arquivo": info,
        "numero_processo": numero_processo.strip(),
        "caminho_processo": caminho_processo.strip()
    }