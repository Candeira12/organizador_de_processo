"""
Configurações gerais da aplicação
"""
import os
from pathlib import Path

# Diretórios
BASE_DIR = os.path.expanduser('/home/gabriel/Área de trabalho/Organizador_de_processo')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ORGANIZADOR_SCRIPT = os.path.expanduser(
    '/home/gabriel/Área de trabalho/Organizador_de_processo.py'
)
DIRETORIO_BASE = "/home/gabriel/Área de trabalho/N8N/variaveis/BAIXAR ARQUIVOS"

# Arquivo de log
LOG_FILE = os.path.join(UPLOAD_FOLDER, 'app.log')

# Extensões e limites
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Timeout
SUBPROCESS_TIMEOUT = 1800  # 30 minutos

# Criar pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)