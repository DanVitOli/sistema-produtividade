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

### 2. Usuários e senhas (Firebase Authentication)

O login usa o **Firebase Authentication por e-mail/senha**; nenhuma senha fica
no código. Cada usuário da tela de login corresponde a uma conta criada no
console do Firebase (Authentication > Usuários), ligada pelo e-mail em
`const credenciais` no `index.html`. Para incluir alguém: crie a conta no
console, acrescente o perfil em `const credenciais` (e em `const assessores`,
se for assessor) e a opção na tela de login, e inclua o UID da conta nas regras
do banco (`database.rules.json`).

A senha é definida pelo próprio usuário pelo link **Esqueci a senha** da tela
de login. A sessão fica guardada no navegador: a pessoa só digita a senha de
novo depois de clicar em Sair.

### 3. Regras do banco

As regras em `database.rules.json` só deixam ler e gravar as contas
autenticadas cuja UID está na lista. Cole-as em Realtime Database > Regras e
publique **depois** de colocar no ar esta versão do sistema e de ajustar o
executor do gabinete para mandar o token (`INTEGRACAO-GABINETE.md`).

Desde 08/11/2026 o nó `gabinete/` (esteira da aba Gabinete) só abre para o juiz
e para a conta do gabinete (gabinete-auto). No Realtime Database uma permissão
dada num nó vale para tudo abaixo dele, por isso a liberação geral deixou de
ficar na raiz e passou para `$outro` (todos os outros nós, com as mesmas quatro
contas de antes). O juiz e a conta do gabinete são reconhecidos pelo e-mail da
conta (`auth.token.email`), além da lista de UIDs; quem preferir pode trocar o
teste do e-mail pelas duas UIDs correspondentes. O repositório não tem
`firebase.json`: as regras são publicadas à mão, colando o arquivo inteiro em
Realtime Database > Regras e clicando em Publicar.

## Hospedagem em endereço próprio

Os caminhos são relativos, então a pasta funciona em qualquer endereço:

- **GitHub Pages (mesmo repositório)**: publicada a branch, o sistema fica em
  `https://SEU-USUARIO.github.io/sistema-produtividade/2vara-civel/`.
- **Repositório/endereço separado**: copie o conteúdo desta pasta para um novo
  repositório e ative o GitHub Pages, ou arraste a pasta em
  <https://app.netlify.com/drop> para obter um endereço próprio na hora.

## Módulos

- **Dashboard**: produtividade diária (12 minutas/assessor: 4 sentenças
  Meta 1, 4 sem movimentação 60+ dias e 4 pedidos/atos), metas semanais
  (Meta 2 e Impulso Processos Antigos) e painéis de acompanhamento quinzenal.
- **Metas do Magistrado**: quadro diário pessoal do juiz (visível apenas no
  login dele): 5 da fila de distribuição automática, 5 da fila de atos
  iniciais e 5 urgentes/pedidos (contadores manuais +/-); 5 sem movimentação
  60+ dias (automática pelas minutas próprias do dia). Total: 20 itens/dia.
- **Registrar Minuta**: registro com múltiplas categorias/metas por minuta,
  disponível para assessores e também para o juiz (produção própria). No
  login do juiz, o formulário exibe o grupo "Metas do Magistrado" (filas de
  distribuição automática e ato inicial) e o registro soma automaticamente
  no quadro diário dele.
- **Balcão Virtual**: pedidos de advogados/partes com prazo de 72h.
- **Metas**: acompanhamento processual por fases, com importação de planilhas
  XLSX, alertas de processos parados e relatórios.
- **Meta 2**: painel do acervo da Meta 2 CNJ (distribuídos até 2022) com
  índice de julgamento em tempo real, alvo de 80%, abas "A julgar"/"Já
  julgados" e registro rápido de sentença (Meta 1 + Meta 2).
- **180/120/100**: painel dos processos sem movimentação (lista da
  Corregedoria) organizados por faixa de dias parados, com cotas por
  sequencial — divisão do gabinete: Juiz 0-1, Gilbert 2-5, Laíse 6-9 — e
  cumprimento automático em
  tempo real quando a minuta do processo é assinada.
- **Calendário e Relatórios**: histórico diário, semanal e mensal.
