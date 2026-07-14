/**
 * Lógica para gerenciamento de processos
 */

let listaProcessos = [];

const inputProcessos = document.getElementById('input-processos');

function inicializarProcessos() {
    // Permitir Enter no input
    inputProcessos.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') adicionarProcesso();
    });
}

function adicionarProcesso() {
    const input = inputProcessos.value.trim();
    
    if (!input) {
        mostrarMensagem('processos', 'error', 'Digite um número de processo ou caminho');
        return;
    }

    if (listaProcessos.includes(input)) {
        mostrarMensagem('processos', 'warning', 'Este processo já está na lista');
        return;
    }

    listaProcessos.push(input);
    inputProcessos.value = '';
    atualizarListaProcessos();
    mostrarMensagem('processos', 'success', 'Processo adicionado');
}

function removerProcesso(indice) {
    listaProcessos.splice(indice, 1);
    atualizarListaProcessos();
}

function limparProcessos() {
    listaProcessos = [];
    atualizarListaProcessos();
    document.getElementById('results-processos').innerHTML = '';
    document.getElementById('results-processos').classList.remove('show');
}

function atualizarListaProcessos() {
    const listDiv = document.getElementById('lista-processos');
    
    if (listaProcessos.length === 0) {
        listDiv.innerHTML = '<p style="color: var(--text-lighter); text-align: center;">Nenhum processo adicionado</p>';
        return;
    }

    listDiv.innerHTML = listaProcessos.map((item, idx) => `
        <div class="item">
            <div class="item-text">${item}</div>
            <button class="item-remove" onclick="removerProcesso(${idx})">Remover</button>
        </div>
    `).join('');
}

async function processarTodos() {
    if (listaProcessos.length === 0) {
        mostrarMensagem('processos', 'error', 'Adicione pelo menos um processo');
        return;
    }

    mostrarLoading('processos');
    mostrarProgresso();
    atualizarProgresso(0);

    const data = await processarListaInputs(listaProcessos);

    if (data.status === 'sucesso' || data.status === 'sucesso_parcial') {
        const resumo = data.resumo;
        mostrarMensagem('processos', 'success', 
            `Processamento concluído: ${resumo.sucessos} sucesso(s), ${resumo.erros} erro(s)`
        );
        atualizarProgresso(100);
        exibirResultados('processos', data);
        listaProcessos = [];
        atualizarListaProcessos();
    } else {
        mostrarMensagem('processos', 'error', data.mensagem);
    }

    esconderLoading('processos');
    esconderProgresso();
}