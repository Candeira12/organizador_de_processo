/**
 * Funções para comunicação com a API
 */

const API_BASE = '/api';

/**
 * Faz upload de um arquivo
 */
async function fazerUploadArquivo(formData) {
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        return await response.json();
    } catch (error) {
        return {
            status: 'erro',
            mensagem: `Erro na requisição: ${error.message}`
        };
    }
}

/**
 * Processa uma lista de inputs
 */
async function processarListaInputs(inputs) {
    try {
        const response = await fetch(`${API_BASE}/processar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ inputs })
        });

        return await response.json();
    } catch (error) {
        return {
            status: 'erro',
            mensagem: `Erro na requisição: ${error.message}`
        };
    }
}

/**
 * Obtém o status do servidor
 */
async function verificarStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        return await response.json();
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        return null;
    }
}