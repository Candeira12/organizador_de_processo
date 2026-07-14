/**
 * Funções de UI compartilhadas
 */

/**
 * Mostra uma mensagem na tela
 */
function mostrarMensagem(tab, tipo, texto) {
    const msgDiv = document.getElementById(`msg-${tab}`);
    msgDiv.textContent = texto;
    msgDiv.className = `message show ${tipo}`;
    
    setTimeout(() => {
        msgDiv.classList.remove('show');
    }, 5000);
}

/**
 * Exibe os resultados de uma operação
 */
function exibirResultados(tab, data) {
    const resultsDiv = document.getElementById(`results-${tab}`);
    let html = '';

    if (tab === 'processos' && data.processos) {
        html += `
            <div style="margin-bottom: 20px; padding: 15px; background: var(--info-light); border-radius: var(--radius-lg);">
                <strong>Resumo:</strong> 
                Total: ${data.resumo.total} | 
                Sucessos: ${data.resumo.sucessos} | 
                Erros: ${data.resumo.erros}
            </div>
        `;

        data.processos.forEach(proc => {
            const classe = proc.status === 'sucesso' ? 'success' : 'error';
            html += `
                <div class="result-item ${classe}">
                    <div class="result-title">${proc.numero_processo || proc.caminho_entrada}</div>
                    <div class="result-content">
                        Status: <strong>${proc.status}</strong><br>
                        ${proc.etapas ? `Etapas: ${proc.etapas.map(e => `${e.nome}(${e.status})`).join(', ')}` : ''}
                    </div>
                </div>
            `;
        });
    } else if (tab === 'upload') {
        html = `
            <div class="result-item success">
                <div class="result-title">Upload Realizado com Sucesso</div>
                <div class="result-content">
                    <strong>Arquivo:</strong> ${data.arquivo.nome_original}<br>
                    <strong>Tamanho:</strong> ${data.arquivo.tamanho_formatado}<br>
                    <strong>Processo:</strong> ${data.numero_processo || data.caminho_processo}
                </div>
            </div>
        `;
    }

    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('show');
}

/**
 * Mostra o loading
 */
function mostrarLoading(tab) {
    document.getElementById(`loading-${tab}`).classList.add('show');
}

/**
 * Esconde o loading
 */
function esconderLoading(tab) {
    document.getElementById(`loading-${tab}`).classList.remove('show');
}

/**
 * Atualiza a barra de progresso
 */
function atualizarProgresso(percentual) {
    document.getElementById('progress-fill').style.width = `${percentual}%`;
}

/**
 * Mostra a barra de progresso
 */
function mostrarProgresso() {
    document.getElementById('progress-bar').style.display = 'block';
}

/**
 * Esconde a barra de progresso
 */
function esconderProgresso() {
    setTimeout(() => {
        document.getElementById('progress-bar').style.display = 'none';
    }, 1000);
}