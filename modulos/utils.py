"""
Funções utilitárias compartilhadas
"""
import re
import os
from datetime import datetime


def extrair_numero_processo(caminho):
    """
    Extrai o número do processo a partir de um caminho.
    Padrão esperado: xxxxxxx-xx.xxxx.x.xx.xxxx
    """
    padrao = re.compile(r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})")
    
    # Tenta encontrar no caminho
    match = padrao.search(caminho)
    if match:
        return match.group(0)
    
    # Tenta no basename
    basename = os.path.basename(caminho.rstrip('/'))
    if padrao.match(basename):
        return basename
    
    return None


def validar_numero_processo(numero):
    """
    Valida se uma string é um número de processo válido
    """
    padrao = re.compile(r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$")
    return bool(padrao.match(numero))


def gerar_nome_arquivo(filename):
    """
    Gera um nome de arquivo com timestamp
    """
    from werkzeug.utils import secure_filename
    
    filename = secure_filename(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{filename}"


def formatar_tamanho_arquivo(bytes_size):
    """
    Formata tamanho de arquivo em formato legível
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f}TB"


def validar_caminho_existe(caminho):
    """
    Valida se um caminho existe
    """
    return os.path.exists(caminho)


def caminho_seguro(caminho_base, caminho_relativo):
    """
    Garante que um caminho relativo não escape do diretório base
    """
    caminho_completo = os.path.abspath(os.path.join(caminho_base, caminho_relativo))
    caminho_base_abs = os.path.abspath(caminho_base)
    
    if not caminho_completo.startswith(caminho_base_abs):
        raise ValueError("Caminho inválido - tentativa de acesso fora do diretório base")
    
    return caminho_completo