# Sistema de Produtividade - 2ª Vara Cível de Palmeira dos Índios

Sistema independente de controle de produtividade do gabinete, derivado do
sistema em operação na vara de origem e adaptado à competência da **2ª Vara
Cível de Palmeira dos Índios/AL**, que **não possui competência criminal, de
execução penal nem de execuções fiscais**.

## O que foi adaptado em relação ao sistema original

- **Removido todo o conteúdo criminal**: SEEU/execução penal, ações penais,
  Tribunal do Júri e violência doméstica (categorias, metas, painéis,
  validações, relatórios e estatísticas).
- **Metas de acompanhamento processual cíveis**:
  - Meta 4 - Improbidade Administrativa
  - Meta 6 - Ações Coletivas
  - Meta - Processos + 10 Anos
  - Meta - Saúde
- **Painéis de acompanhamento quinzenal**: Conhecimento > 10 anos, Fazenda
  Pública, Ações de Saúde e Ações Ambientais.
- **Balcão Virtual**: classes "Cível" e "Fazenda Pública" (antes
  Cível/Criminal); categoria "Crime" substituída por "Fazenda Pública".
- **"Meta 10" renomeada** para "Impulso Processos Antigos" (1 minuta/semana em
  qualquer dos processos mais antigos), disponível para todos os assessores.
- **Usuários da unidade** (`juiz`, `gilbert`, `laise`) sem exclusividades de
  categoria por assessor.
- **Banco de dados próprio**: o sistema NÃO compartilha o Firebase da vara de
  origem; exige um projeto Firebase novo (ver abaixo).
- Identidade visual própria (ciano), PWA com manifest/ícone/service worker
  próprios e caminhos relativos, permitindo hospedagem em qualquer endereço
  (subpasta do GitHub Pages, Netlify etc.).

## Configuração obrigatória antes do uso

### 1. Criar o projeto Firebase (banco de dados independente)

1. Acesse <https://console.firebase.google.com> e crie um projeto novo
   (ex.: `produtividade-2vara-civel`).
2. No menu **Criação > Realtime Database**, clique em **Criar banco de dados**
   (modo de teste para começar; depois configure regras de segurança).
3. Em **Configurações do projeto > Geral > Seus apps**, registre um app Web
   (`</>`), sem Hosting.
4. Copie o objeto `firebaseConfig` exibido e substitua o bloco de
   placeholders no `index.html` desta pasta (procure por
   `CONFIGURAÇÃO OBRIGATÓRIA`).

### 2. Personalizar usuários e senhas

No `index.html`, localize `const credenciais` e ajuste nomes, logins e senhas
da equipe. As senhas padrão de fábrica são:

| Usuário   | Nome                          | Senha             |
|-----------|-------------------------------|-------------------|
| `juiz`    | Danilo Vital de Oliveira      | `Juiz2VC@2026!`   |
| `gilbert` | Gilbert Juliano de Sena Lúcio | `Gilbert2VC@2026!`|
| `laise`   | Laíse Vital da Silva Nunes    | `Laise2VC@2026!`  |

**Troque essas senhas antes de colocar em produção.** Se alterar os nomes de
exibição, ajuste também `const assessores` (logo abaixo no mesmo arquivo) e as
opções da tela de login.

## Hospedagem em endereço próprio

Os caminhos são relativos, então a pasta funciona em qualquer endereço:

- **GitHub Pages (mesmo repositório)**: publicada a branch, o sistema fica em
  `https://SEU-USUARIO.github.io/sistema-produtividade/2vara-civel/`.
- **Repositório/endereço separado**: copie o conteúdo desta pasta para um novo
  repositório e ative o GitHub Pages, ou arraste a pasta em
  <https://app.netlify.com/drop> para obter um endereço próprio na hora.

## Módulos

- **Dashboard**: produtividade diária (10 minutas/assessor), metas semanais
  (Meta 2 e Impulso Processos Antigos) e painéis de acompanhamento quinzenal.
- **Registrar Minuta**: registro com múltiplas categorias/metas por minuta.
- **Balcão Virtual**: pedidos de advogados/partes com prazo de 72h.
- **Metas**: acompanhamento processual por fases, com importação de planilhas
  XLSX, alertas de processos parados e relatórios.
- **Calendário e Relatórios**: histórico diário, semanal e mensal.
