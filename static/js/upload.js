/**
 * Lógica para gerenciamento de upload de arquivos
 * Suporta upload único e upload em lote com extração automática de números de processo
 */

// Elementos DOM
const fileLabel = document.getElementById('file-label');
const fileInput = document.getElementById('arquivo');
const fileName = document.getElementById('file-name');

const fileLabelBatch = document.getElementById('file-label-batch');
const fileInputBatch = document.getElementById('arquivo-lote');
const fileListBatch = document.getElementById('file-list-batch');

// Modo atual
let modoUploadAtual = 'single';

/**
 * Inicializa listeners de upload
 */
function inicializarUpload() {
    // === MODO ÚNICO ===
    fileLabel.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileLabel.classList.add('dragover');
    });

    fileLabel.addEventListener('dragleave', () => {
        fileLabel.classList.remove('dragover');
    });

    fileLabel.addEventListener('drop', (e) => {
        e.preventDefault();
        fileLabel.classList.remove('dragover');
        fileInput.files = e.dataTransfer.files;
        atualizarNomeArquivo();
    });

    fileInput.addEventListener('change', atualizarNomeArquivo);

    // === MODO LOTE ===
    fileLabelBatch.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileLabelBatch.classList.add('dragover');
    });

    fileLabelBatch.addEventListener('dragleave', () => {
        fileLabelBatch.classList.remove('dragover');
    });

    fileLabelBatch.addEventListener('drop', (e) => {
        e.preventDefault();
        fileLabelBatch.classList.remove('dragover');
        fileInputBatch.files = e.dataTransfer.files;
        atualizarListaArquivos();
    });

    fileInputBatch.addEventListener('change', atualizarListaArquivos);
}

/**
 * Alterna entre modo único e modo lote
 */
function alterarModoUpload(modo) {
    modoUploadAtual = modo;

    // Atualizar botões
    document.getElementById('mode-single').classList.toggle('active', modo === 'single');
    document.getElementById('mode-batch').classList.toggle('active', modo === 'batch');

    // Atualizar conteúdo
    document.getElementById('upload-single').classList.toggle('active', modo === 'single');
    document.getElementById('upload-batch').classList.toggle('active', modo === 'batch');
}

/**
 * Atualiza o nome do arquivo exibido (modo único)
 */
function atualizarNomeArquivo() {
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
        fileName.textContent = `✓ ${file.name} (${sizeMB}MB)`;
    } else {
        fileName.textContent = '';
    }
}

/**
 * Atualiza a lista de arquivos exibida (modo lote)
 */
function atualizarListaArquivos() {
    const files = fileInputBatch.files;
    
    if (files.length === 0) {
        fileListBatch.innerHTML = '';
        return;
    }

    let html = '<div class="file-list-container">';
    let totalSize = 0;

    for (let file of files) {
        totalSize += file.size;
        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
        const numeroProcesso = extrairNumeroProcessoDoNomeArquivo(file.name);
        
        html += `
            <div class="file-list-item">
                <div class="file-info">
                    <div class="file-name">📄 ${file.name}</div>
                    <div class="file-details">
                        <span class="file-size">${sizeMB}MB</span>
                        ${numeroProcesso ? 
                            `<span class="file-process">📋 ${numeroProcesso}</span>` : 
                            `<span class="file-process error">⚠️ Número não identificado</span>`
                        }
                    </div>
                </div>
            </div>
        `;
    }

    const totalMB = (totalSize / 1024 / 1024).toFixed(2);
    html += `
        <div style="padding: 10px; background: var(--info-light); border-radius: var(--radius-md); margin-top: 10px;">
            <strong>Total:</strong> ${files.length} arquivo(s) | ${totalMB}MB
        </div>
    </div>`;

    fileListBatch.innerHTML = html;
}

/**
 * Extrai o número do processo do nome do arquivo
 * Esperado: xxxxxxx-xx.xxxx.x.xx.xxxx (ou com sufixos adicionais)
 */
function extrairNumeroProcessoDoNomeArquivo(filename) {
    // Padrão: xxxxxxx-xx.xxxx.x.xx.xxxx
    const padrao = /(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})/;
    const match = filename.match(padrao);
    return match ? match[1] : null;
}

/**
 * Valida número de processo
 */
function validarNumeroProcesso(numero) {
    const padrao = /^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$/;
    return padrao.test(numero);
}

/**
 * Upload único com validação manual de número de processo
 */
async function fazerUpload() {
    const arquivo = fileInput.files[0];
    const numeroProcesso = document.getElementById('numero-processo')?.value.trim() || '';
    const caminhoProcesso = document.getElementById('caminho-processo')?.value.trim() || '';

    if (!arquivo) {
        mostrarMensagem('upload', 'error', '❌ Selecione um arquivo');
        return;
    }

    if (!numeroProcesso && !caminhoProcesso) {
        mostrarMensagem('upload', 'error', '❌ Forneça número do processo OU caminho completo');
        return;
    }

    if (numeroProcesso && !validarNumeroProcesso(numeroProcesso)) {
        mostrarMensagem('upload', 'error', '❌ Formato de número de processo inválido');
        return;
    }

    const formData = new FormData();
    formData.append('arquivo', arquivo);
    formData.append('numero_processo', numeroProcesso);
    formData.append('caminho_processo', caminhoProcesso);

    mostrarLoading('upload');

    try {
        const data = await fazerUploadArquivo(formData);

        if (data.status === 'sucesso') {
            mostrarMensagem('upload', 'success', '✅ ' + data.mensagem);
            limparUpload();
            exibirResultadosUpload(data);
        } else {
            mostrarMensagem('upload', 'error', '❌ ' + data.mensagem);
        }
    } catch (error) {
        mostrarMensagem('upload', 'error', '❌ Erro ao processar upload: ' + error.message);
    } finally {
        esconderLoading('upload');
    }
}

/**
 * Upload em lote com extração automática de números de processo
 */
async function fazerUploadLote() {
    const files = fileInputBatch.files;

    if (files.length === 0) {
        mostrarMensagem('upload', 'error', '❌ Selecione pelo menos um arquivo');
        return;
    }

    // Validar que todos os arquivos têm número de processo
    const arquivosInvalidos = [];
    for (let file of files) {
        if (!extrairNumeroProcessoDoNomeArquivo(file.name)) {
            arquivosInvalidos.push(file.name);
        }
    }

    if (arquivosInvalidos.length > 0) {
        mostrarMensagem(
            'upload', 
            'error', 
            `❌ Arquivos sem número de processo identificado: ${arquivosInvalidos.join(', ')}`
        );
        return;
    }

    mostrarLoading('upload');
    mostrarProgressoUpload();

    const resultados = {
        sucessos: 0,
        erros: 0,
        detalhes: [],
        totalArquivos: files.length
    };

    try {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const numeroProcesso = extrairNumeroProcessoDoNomeArquivo(file.name);

            // Atualizar progresso
            const percentual = Math.round((i / files.length) * 100);
            atualizarProgressoUpload(percentual);

            const formData = new FormData();
            formData.append('arquivo', file);
            formData.append('numero_processo', numeroProcesso);
            formData.append('caminho_processo', '');

            try {
                const data = await fazerUploadArquivo(formData);

                if (data.status === 'sucesso') {
                    resultados.sucessos++;
                    resultados.detalhes.push({
                        arquivo: file.name,
                        numero: numeroProcesso,
                        status: 'sucesso',
                        mensagem: data.mensagem
                    });
                } else {
                    resultados.erros++;
                    resultados.detalhes.push({
                        arquivo: file.name,
                        numero: numeroProcesso,
                        status: 'erro',
                        mensagem: data.mensagem
                    });
                }
            } catch (error) {
                resultados.erros++;
                resultados.detalhes.push({
                    arquivo: file.name,
                    numero: numeroProcesso,
                    status: 'erro',
                    mensagem: error.message
                });
            }

            // Pequena pausa entre requisições
            await new Promise(resolve => setTimeout(resolve, 100));
        }

        // Finalizar progresso
        atualizarProgressoUpload(100);

        // Exibir resumo
        if (resultados.sucessos > 0) {
            mostrarMensagem(
                'upload', 
                'success', 
                `✅ Processamento concluído: ${resultados.sucessos} sucesso(s), ${resultados.erros} erro(s)`
            );
            limparUploadLote();
        } else {
            mostrarMensagem('upload', 'error', '❌ Nenhum arquivo foi processado com sucesso');
        }

        exibirResultadosUploadLote(resultados);

    } catch (error) {
        mostrarMensagem('upload', 'error', '❌ Erro ao processar lote: ' + error.message);
    } finally {
        esconderLoading('upload');
        esconderProgressoUpload();
    }
}

/**
 * Exibe resultados de upload único
 */
function exibirResultadosUpload(data) {
    const resultsDiv = document.getElementById('results-upload');
    
    const html = `
        <div class="result-item success">
            <div class="result-title">✅ Upload Realizado com Sucesso</div>
            <div class="result-content">
                <strong>Arquivo:</strong> ${data.arquivo.nome_original}<br>
                <strong>Tamanho:</strong> ${data.arquivo.tamanho_formatado}<br>
                <strong>Processo:</strong> ${data.numero_processo || data.caminho_processo}<br>
                <strong>Caminho:</strong> <code>${data.arquivo.caminho}</code>
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('show');
}

/**
 * Exibe resultados de upload em lote
 */
function exibirResultadosUploadLote(resultados) {
    const resultsDiv = document.getElementById('results-upload');
    
    let html = `
        <div style="margin-bottom: 20px; padding: 15px; background: var(--info-light); border-radius: var(--radius-lg);">
            <strong>📊 Resumo do Processamento:</strong><br>
            Total: ${resultados.totalArquivos} | 
            ✅ Sucessos: ${resultados.sucessos} | 
            ❌ Erros: ${resultados.erros}
        </div>
    `;

    resultados.detalhes.forEach(detalhe => {
        const classe = detalhe.status === 'sucesso' ? 'success' : 'error';
        const icone = detalhe.status === 'sucesso' ? '✅' : '❌';
        
        html += `
            <div class="result-item ${classe}">
                <div class="result-title">${icone} ${detalhe.arquivo}</div>
                <div class="result-content">
                    <strong>Processo:</strong> ${detalhe.numero}<br>
                    <strong>Status:</strong> ${detalhe.status}<br>
                    <strong>Mensagem:</strong> ${detalhe.mensagem}
                </div>
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('show');
}

/**
 * Mostra barra de progresso
 */
function mostrarProgressoUpload() {
    document.getElementById('progress-bar-upload').style.display = 'flex';
    document.getElementById('progress-fill-upload').style.width = '0%';
    document.getElementById('progress-text-upload').textContent = '0%';
}

/**
 * Atualiza barra de progresso
 */
function atualizarProgressoUpload(percentual) {
    document.getElementById('progress-fill-upload').style.width = `${percentual}%`;
    document.getElementById('progress-text-upload').textContent = `${percentual}%`;
}

/**
 * Esconde barra de progresso
 */
function esconderProgressoUpload() {
    setTimeout(() => {
        document.getElementById('progress-bar-upload').style.display = 'none';
    }, 1000);
}

/**
 * Limpa upload único
 */
function limparUpload() {
    fileInput.value = '';
    fileName.textContent = '';
    document.getElementById('results-upload').innerHTML = '';
    document.getElementById('results-upload').classList.remove('show');
}

/**
 * Limpa upload em lote
 */
function limparUploadLote() {
    fileInputBatch.value = '';
    fileListBatch.innerHTML = '';
    document.getElementById('results-upload').innerHTML = '';
    document.getElementById('results-upload').classList.remove('show');
}