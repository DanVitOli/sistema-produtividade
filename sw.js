// 08/11/2026: service worker de desinstalação do sistema legado da raiz.
// O sistema antigo foi retirado do ar (a raiz só redireciona para ./2vara-civel/).
// Navegadores que já tinham o SW antigo instalado baixam esta versão na próxima
// verificação de atualização: ela apaga apenas os caches do próprio SW antigo
// (prefixo "produtividade-judicial-"; os da 2ª Vara não são tocados), se desregistra
// e recarrega as abas que controlava, que então caem no redirecionamento.
const PREFIXO_CACHE = 'produtividade-judicial-';

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const nomes = await caches.keys();
    await Promise.all(nomes.filter((n) => n.startsWith(PREFIXO_CACHE)).map((n) => caches.delete(n)));
    await self.registration.unregister();
    const abas = await self.clients.matchAll({ type: 'window' });
    abas.forEach((aba) => { try { aba.navigate(aba.url); } catch (e) { /* aba já fechada */ } });
  })());
});
