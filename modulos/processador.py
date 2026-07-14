"""
Lógica para processamento de caminhos, números de processo e uploads com organização
"""
import os
import logging
import shutil
import re
from pathlib import Path
from modulos.config import DIRETORIO_BASE
from modulos.utils import extrair_numero_processo, validar_numero_processo
from modulos.organizador import executar_organizador

logger = logging.getLogger(__name__)


def extrair_numero_do_filename(filename):
    """
    Extrai o número do processo do nome do arquivo.
    Esperado: xxxxxxx-xx.xxxx.x.xx.xxxx (pode ter sufixos)
    Exemplo: 0800072-85.2026.8.18.0059-1783948749299-2289310-processo.pdf
    Retorna: 0800072-85.2026.8.18.0059
    """
    padrao = re.compile(r'(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})')
    match = padrao.search(filename)
    return match.group(1) if match else None


def validar_e_criar_pasta_processo(numero_processo):
    """
    Valida e gerencia a pasta do processo em DIRETORIO_BASE
    Se existir: deleta e recria
    Se não existir: cria
    
    Retorna: (sucesso: bool, caminho_pasta: str, mensagem: str)
    """
    if not validar_numero_processo(numero_processo):
        return False, None, f"Número de processo inválido: {numero_processo}"
    
    # Construir caminho da pasta
    caminho_pasta = os.path.join(DIRETORIO_BASE, numero_processo)
    
    try:
        # Se existe, deletar
        if os.path.exists(caminho_pasta):
            logger.info(f"Deletando pasta existente: {caminho_pasta}")
            shutil.rmtree(caminho_pasta)
        
        # Criar pasta
        os.makedirs(caminho_pasta, exist_ok=True)
        logger.info(f"Pasta criada: {caminho_pasta}")
        
        return True, caminho_pasta, f"Pasta preparada: {caminho_pasta}"
    
    except Exception as e:
        erro = f"Erro ao gerenciar pasta {caminho_pasta}: {str(e)}"
        logger.error(erro)
        return False, None, erro


def mover_arquivo_para_pasta_processo(arquivo_path, numero_processo, caminho_pasta_processo):
    """
    Move o arquivo para a pasta do processo
    
    Retorna: (sucesso: bool, novo_caminho: str, mensagem: str)
    """
    try:
        if not os.path.exists(arquivo_path):
            return False, None, f"Arquivo não encontrado: {arquivo_path}"
        
        if not os.path.exists(caminho_pasta_processo):
            return False, None, f"Pasta de processo não existe: {caminho_pasta_processo}"
        
        # Usar o número do processo como nome do arquivo na pasta
        extensao = os.path.splitext(arquivo_path)[1]
        novo_nome = f"{numero_processo}{extensao}"
        novo_caminho = os.path.join(caminho_pasta_processo, novo_nome)
        
        # Mover arquivo
        shutil.move(arquivo_path, novo_caminho)
        logger.info(f"Arquivo movido: {arquivo_path} -> {novo_caminho}")
        
        return True, novo_caminho, f"Arquivo movido com sucesso"
    
    except Exception as e:
        erro = f"Erro ao mover arquivo: {str(e)}"
        logger.error(erro)
        return False, None, erro


def processar_upload_com_organizacao(arquivo_path, numero_processo):
    """
    Processa upload com a lógica completa:
    1. Valida número do processo
    2. Cria/recria pasta em DIRETORIO_BASE
    3. Move arquivo para a pasta
    4. Executa Organizador_de_processo.py
    
    Retorna: dict com status, mensagem e resultados
    """
    logger.info(f"Iniciando processamento de upload: {numero_processo}")
    
    # Passo 1: Validar número do processo
    if not validar_numero_processo(numero_processo):
        return {
            "status": "erro",
            "mensagem": f"Número de processo inválido: {numero_processo}",
            "numero_processo": numero_processo
        }
    
    # Passo 2: Validar e criar/recriar pasta
    sucesso, caminho_pasta, msg_pasta = validar_e_criar_pasta_processo(numero_processo)
    if not sucesso:
        return {
            "status": "erro",
            "mensagem": msg_pasta,
            "numero_processo": numero_processo
        }
    
    # Passo 3: Mover arquivo para pasta
    sucesso, novo_caminho, msg_move = mover_arquivo_para_pasta_processo(
        arquivo_path, 
        numero_processo, 
        caminho_pasta
    )
    if not sucesso:
        return {
            "status": "erro",
            "mensagem": msg_move,
            "numero_processo": numero_processo
        }
    
    # Passo 4: Executar Organizador_de_processo.py
    logger.info(f"Executando organizador com: {novo_caminho}")
    resultado_organizador = executar_organizador([novo_caminho])
    
    # Retornar resultado com informações completas
    return {
        "status": resultado_organizador.get("status", "sucesso"),
        "mensagem": resultado_organizador.get("mensagem", "Processamento concluído"),
        "numero_processo": numero_processo,
        "caminho_arquivo": novo_caminho,
        "caminho_pasta": caminho_pasta,
        "resultado_organizador": resultado_organizador
    }


def converter_inputs_para_caminhos(inputs):
    """
    Converte uma lista de números de processo ou caminhos para caminhos completos
    Retorna: (sucesso, lista_de_caminhos_ou_erro)
    """
    caminhos_finais = []
    erros = []
    
    for item in inputs:
        item = item.strip()
        
        if not item:
            continue
        
        # Verifica se é um caminho (contém /)
        if '/' in item:
            # É um caminho completo
            if os.path.exists(item):
                caminhos_finais.append(item)
                logger.info(f"Caminho completo adicionado: {item}")
            else:
                erro = f"Caminho não encontrado: {item}"
                erros.append(erro)
                logger.warning(erro)
        
        else:
            # Tenta tratar como número de processo
            if validar_numero_processo(item):
                caminho_expandido = os.path.join(DIRETORIO_BASE, item)
                
                if os.path.exists(caminho_expandido):
                    caminhos_finais.append(caminho_expandido)
                    logger.info(f"Número de processo expandido: {item} -> {caminho_expandido}")
                else:
                    erro = f"Caminho não encontrado para o processo: {item}"
                    erros.append(erro)
                    logger.warning(erro)
            else:
                erro = f"Formato inválido: {item}"
                erros.append(erro)
                logger.warning(erro)
    
    if erros and not caminhos_finais:
        return False, {
            "status": "erro",
            "mensagem": "Nenhum caminho válido foi encontrado",
            "erros": erros,
            "sugestao": f"Verifique o diretório base: {DIRETORIO_BASE}"
        }
    
    if erros:
        logger.warning(f"Alguns caminhos falharam, mas {len(caminhos_finais)} foram válidos")
    
    return True, caminhos_finais


def processar_lista_inputs(inputs):
    """
    Processa uma lista de inputs (números ou caminhos)
    """
    # Validar inputs
    if not inputs:
        return {
            "status": "erro",
            "mensagem": "Nenhum número de processo ou caminho foi fornecido"
        }
    
    # Converter para caminhos
    sucesso, resultado = converter_inputs_para_caminhos(inputs)
    
    if not sucesso:
        return resultado
    
    caminhos_finais = resultado
    
    logger.info(f"Iniciando processamento de {len(caminhos_finais)} caminho(s)")
    
    # Executar organizador
    resultado_organizador = executar_organizador(caminhos_finais)
    
    return resultado_organizador