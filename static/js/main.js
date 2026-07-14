/**
 * Orquestrador Principal - Inicializa todos os módulos
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Inicializando Organizador de Processo...');
    
    // Inicializar módulos
    inicializarAbas();
    inicializarUpload();
    inicializarProcessos();
    
    // Verificar status do servidor
    console.log('📡 Verificando status do servidor...');
    const status = await verificarStatus();
    if (status) {
        console.log('✓ Servidor online', status);
    } else {
        console.error('✗ Erro ao conectar com o servidor');
    }
    
    console.log('✓ Aplicação pronta!');
});