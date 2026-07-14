/**
 * Gerenciamento de Abas
 */

function inicializarAbas() {
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Remover classe active de todos
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Adicionar classe active ao clicado
            button.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        });
    });
}

/**
 * Muda para uma aba específica
 */
function mudarAba(tabName) {
    const button = document.querySelector(`[data-tab="${tabName}"]`);
    if (button) {
        button.click();
    }
}