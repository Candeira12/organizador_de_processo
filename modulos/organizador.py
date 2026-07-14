"""
Interface de comunicação com o script Organizador_de_processo.py
"""
import sys
import subprocess
import json
import logging
from modulos.config import ORGANIZADOR_SCRIPT, SUBPROCESS_TIMEOUT

logger = logging.getLogger(__name__)


def executar_organizador(caminhos):
    """
    Executa o script Organizador_de_processo.py com os caminhos fornecidos
    """
    if not caminhos:
        return {
            "status": "erro",
            "mensagem": "Nenhum caminho foi fornecido"
        }
    
    try:
        comando = [sys.executable, ORGANIZADOR_SCRIPT] + caminhos
        
        logger.info(f"Executando organizador com {len(caminhos)} caminho(s)")
        
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT
        )
        
        if resultado.returncode == 0:
            try:
                output = json.loads(resultado.stdout)
                logger.info(f"Organizador retornou com sucesso")
                return output
            
            except json.JSONDecodeError:
                logger.error("Erro ao parsear JSON do organizador")
                return {
                    "status": "erro",
                    "mensagem": "Erro ao parsear resposta do organizador",
                    "saida_bruta": resultado.stdout
                }
        
        else:
            logger.error(f"Organizador retornou com erro: {resultado.stderr}")
            return {
                "status": "erro",
                "mensagem": "Erro ao executar o organizador",
                "stderr": resultado.stderr,
                "stdout": resultado.stdout
            }
    
    except subprocess.TimeoutExpired:
        logger.error("Timeout ao executar o organizador")
        return {
            "status": "erro",
            "mensagem": f"Timeout ao executar o organizador ({SUBPROCESS_TIMEOUT}s)"
        }
    
    except Exception as e:
        logger.error(f"Exceção ao executar organizador: {str(e)}")
        return {
            "status": "erro",
            "mensagem": f"Erro ao executar: {str(e)}"
        }