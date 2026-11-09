# Integração automática Gabinete → Sistema

O executor do gabinete grava as minutas **direto no banco do sistema** pela
REST do Firebase. A sessão do juiz aberta no sistema completa sozinha os
efeitos (categorias dos painéis Meta 2 e 180/120/100, sincronização das abas,
baixa no Balcão e contadores das metas do magistrado) e publica o snapshot do
Painel em `snapshotPainel/`. **Nenhum copiar/colar é necessário.**

Base: `https://produtividade-2vara-civel-default-rtdb.firebaseio.com`

## 0. Autenticação (obrigatória)

O banco só aceita contas autenticadas da lista de `database.rules.json`. O
executor usa a conta **gabinete-auto** (danilooliveira@tjal.jus.br), com as
credenciais em `firebase-credencial.json` na máquina do executor (nunca no
repositório):

1. `POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=<apiKey>`
   com `{"email", "password", "returnSecureToken": true}` → `idToken`
   (vale 1 hora) e `refreshToken`.
2. Toda chamada ao banco leva `?auth=<idToken>` no fim da URL.
3. Para renovar: `POST https://securetoken.googleapis.com/v1/token?key=<apiKey>`
   com `grant_type=refresh_token&refresh_token=<refreshToken>` → novo
   `id_token`. Renove alguns minutos antes de vencer ou ao receber HTTP 401.

O módulo `firebase_auth.py` faz os três passos.

## 1. Registrar minuta da IA (pendente de revisão/assinatura)

`PUT /minutas/painel-ia-<painelId>.json` **condicional**: primeiro
`GET` com o cabeçalho `X-Firebase-ETag: true`; só se o nó vier vazio, `PUT`
com `if-match: <ETag>` (resposta 412 = alguém criou antes; não regrave).
**Nunca** regrave um registro existente com `PUT`: isso apagava a trava de
efeitos e o sistema reaplicava metas e baixas. Registro existente só recebe
`PATCH` de campos pontuais (ver item 2).

```json
{
  "assessorId": "claude_ia",
  "assessorNome": "Claude (IA) · Painel do Gabinete",
  "numeroProcesso": "0700000-00.2024.8.02.0046",
  "tipoMinuta": "Despacho",
  "categorias": ["sem_movimento"],
  "observacoes": "Minuta elaborada pelo Claude (IA) no Painel do Gabinete e aprovada pelo juiz para revisão.",
  "substituicao": false,
  "status": "pendente",
  "data": "2026-10-20",
  "timestamp": "14:32:00",
  "createdAt": {".sv": "timestamp"},
  "painelId": "<painelId>",
  "origem": "gabinete-auto"
}
```

## 2. Lançar minuta assinada em nome do juiz

Quando o juiz marca a minuta como assinada no Painel:

`PUT /minutas/painel-<painelId>.json`, também **condicional** (como no item 1)
— é a mesma chave usada pelo botão manual "Lançar assinadas"; se o juiz já
lançou pelo botão, o nó existe e o executor não grava nada.

```json
{
  "assessorId": "juiz",
  "assessorNome": "Danilo Vital de Oliveira",
  "numeroProcesso": "0700000-00.2024.8.02.0046",
  "tipoMinuta": "Sentença",
  "categorias": ["meta1", "meta2"],
  "observacoes": "Minuta elaborada com o Claude (IA) no Painel do Gabinete, revisada e assinada pelo juiz.",
  "substituicao": false,
  "status": "assinada",
  "data": "2026-10-20",
  "timestamp": "14:50:00",
  "createdAt": {".sv": "timestamp"},
  "painelId": "<painelId>",
  "origem": "gabinete-auto"
}
```

Se a minuta pendente (item 1) já existia e foi assinada depois, o executor pode
simplesmente atualizar: `PATCH /minutas/painel-ia-<painelId>.json` com
`{"status": "assinada"}`.

## 3. Ler o snapshot do sistema (para exibir no Painel)

`GET /snapshotPainel.json`

O sistema republica esse nó automaticamente (~4 s após qualquer mudança,
enquanto houver uma sessão do juiz aberta). Mesmo formato
`produtividade-2vc/snapshot` que o botão "Copiar para o sistema" gerava, com o
campo extra `publicadoEm`.

## Regras e observações

- **Campos obrigatórios**: `numeroProcesso` (formato CNJ), `tipoMinuta`
  (`Despacho` | `Decisão` | `Sentença`), `categorias` (ao menos uma válida;
  `meta2` exige Sentença), `status`, `data` (AAAA-MM-DD, fuso de Maceió),
  `painelId` (`[A-Za-z0-9_-]`, até 120), `origem: "gabinete-auto"`.
- **Categorias válidas**: `meta1`, `meta2`, `meta10`, `sem_movimento`,
  `outros`, `alem_meta`, `juiz_distribuicao`, `juiz_ato_inicial` (as duas
  últimas só em minutas do juiz), além das categorias de painel
  (`conhecimento_10anos`, `fazenda_publica`, `acoes_saude`, `acoes_ambientais`).
  **Não** inclua as categorias derivadas dos painéis Meta 2/180-120-100: o
  sistema acrescenta sozinho ao processar.
- **Balcão**: se a minuta atende um pedido do Balcão, inclua
  `"pedidoBalcaoId": "<id>"` (os ids dos pendentes vêm no snapshot) — o
  sistema dá baixa sozinho.
- **Efeitos**: a trava de efeitos fica em `efeitosGabinete/<id da minuta>`,
  gravada só pelo sistema (o campo `efeitosAplicados` na minuta é mantido
  apenas para leitura). Nunca envie nenhum dos dois. Os contadores das metas do magistrado só são incrementados para
  minutas com `assessorId: "juiz"`.
- Exemplo com curl:

```bash
curl -sS -X PUT \
  "https://produtividade-2vara-civel-default-rtdb.firebaseio.com/minutas/painel-ia-ABC123.json?auth=$ID_TOKEN" \
  -H 'Content-Type: application/json' \
  -d @minuta.json
```

## Esteira do gabinete no sistema (desde 08/11/2026)

O Painel do Gabinete (artifact do claude.ai) foi incorporado ao sistema como a aba
**Gabinete**, visível e utilizável só no login do juiz. Os dados da esteira saíram do
armazenamento do artifact e passaram a morar neste banco, no nó `gabinete/`. O artifact
será aposentado.

### Acesso

`gabinete/` só abre (leitura e gravação) para o juiz e para a conta **gabinete-auto**
(`database.rules.json`). Os assessores não leem nem gravam nada ali; os demais nós
continuam com as quatro contas de antes. As gravações aceitas são as de sempre da REST:
`PUT` condicional (`if-match`) e `PATCH` multi-caminho no nível de `gabinete/processos`
(ex.: `{"<id>/prod/status": "lancada"}`). Não há `.validate` por campo.
Índices: `gabinete/processos` tem `.indexOn` em `execStatus` e `lancarStatus`
(ex.: `?orderBy="execStatus"&equalTo="fila"`).

### `gabinete/processos/<id>`

Um nó por processo, com o mesmo objeto de cada documento da coleção `processos` do
artifact e o mesmo id (na migração, a chave é saneada: `. # $ [ ] /` viram `_`). Datas e
horas são ISO 8601 (`toISOString()`), exceto `concluso` (AAAA-MM-DD).

| Campo | Quem grava | Conteúdo |
|---|---|---|
| `numero` | aba | número CNJ com máscara (`validarCNJ`), sufixo `/0001` opcional |
| `classe`, `notas` | aba | texto livre (notas = orientações ao Claude) |
| `concluso` | aba | AAAA-MM-DD |
| `materia` | aba | `civel`, `consumidor`, `familia`, `sucessoes`, `execucao`, `fazenda`, `contratos`, `possessorias` |
| `especie` | aba | `auto`, `despacho`, `decisao`, `liminar`, `sentenca`, `embargos`, `inv-saneadora`, `inv-homologa` |
| `meta2`, `biblio`, `juris`, `exemplo` | aba | booleanos |
| `etapa` | aba / executor | `fila`, `minuta`, `revisada`, `assinada` (o comando também trata `baixado` e `firac`) |
| `modo`, `rigor`, `esforco` | aba | `minuta`/`chat`, `rigoroso`/`livre`, 1 a 5 |
| `execStatus` | aba / executor | `""` (não pedido), `fila`, `executando`, `concluido`, `erro` |
| `exec` | aba / executor | `{pedidoEm, comando, loteId, iniciadoEm, concluidoEm, fase, resumo, ficha, arquivo, erro, aviso}`; `aviso: "captcha"` = pausado pelo captcha (o processo volta à fila); a aba também reconhece `aviso: "esaj-expirado"` (ou erro que fale em sessão expirada) como e-SAJ expirado |
| `atoGerado` | executor | `Despacho`, `Decisão` ou `Sentença`: o que a minuta realmente é |
| `minutaAnterior` | executor | caminho da minuta anterior, quando houver |
| `origem` | aba / executor | `{tipo: "lote" \| "pasta" \| "meta2" \| "meta180" \| "balcao", pedidoBalcaoId}` (ausente no cadastro avulso) |
| `prod` | aba / executor | `{status, tipo, categorias, solicitadoEm, enviadaEm, lancadaEm, lancadoPor, minutaId, erro}` |
| `lancarStatus` | aba / executor | `ok`, `pendente`, `duplicidade` |
| `arquivado`, `arquivadoEm` | aba | `true`/`false` sobrepõe a regra automática do Arquivo |
| `criadoEm`, `atualizadoEm` | aba / executor | ISO |

Regras que a aba aplica (as mesmas do Painel):

- **Pedido de execução**: a aba grava `execStatus: "fila"` e um `exec` novo com o
  `comando` (o texto que o executor roda). Cada ativação processa no máximo 6 (Meta 2
  primeiro, depois os mais antigos).
- **Arquivo**: sai da esteira a lançada no sistema 1 dia depois de `prod.lancadaEm`, a
  minuta da pasta que já chegou lançada (`origem.tipo == "pasta"` com `prod.lancadoPor`) e
  a arquivada à mão. `arquivado` true/false sobrepõe. Nada é apagado.
- **Parada**: minuta pronta e não revisada há mais de 30 dias (`exec.concluidoEm`) ganha
  "parada há X dias" e entra no filtro Atrasados (com os conclusos há mais de 60 dias).
- **Excluir do painel** (com confirmação): remove `gabinete/processos/<id>`, como o Painel
  fazia. As minutas do sistema não são tocadas. Processo em execução não é excluído.
- **`prod` é sempre mesclado**: a aba grava campo a campo (`prod/status`,
  `prod/lancadaEm`…) e nunca substitui o objeto. O executor deve fazer o mesmo.
- **Campos ausentes**: o Firebase descarta `{}` e `[]`; a aba trata `exec`, `prod`,
  `categorias` e os demais campos ausentes como vazios. O executor deve fazer o mesmo.

### Assinar e lançar / Aprovar para revisão (gravados pela aba)

- **Assinar e lançar** usa a mesma função do botão "Lançar assinadas do Painel": valida
  número, tipo e categorias; se já existe minuta com o mesmo `painelId` (por exemplo
  `painel-ia-<id>` do Claude IA, ou `painel-<id>` gravada pelo executor), só aplica a
  assinatura ou a correção de ato/categorias (`update`, nunca regrava); senão confere a
  **duplicidade** (outra minuta ativa do mesmo processo, de qualquer autor, nos últimos 7
  dias) e, se não houver, cria `minutas/painel-<id>` em nome do juiz, já assinada, por
  **transação condicional** (só se a chave estiver vazia; se alguém criou antes, nada é
  sobrescrito), com `origem: "painel-gabinete"`, a trava em `efeitosGabinete/painel-<id>` e
  os efeitos do Registrar Minuta. No processo grava `etapa: "assinada"`,
  `lancarStatus: "ok"`, `prod/status: "lancada"`, `prod/lancadaEm`, `prod/minutaId`,
  `prod/tipo`, `prod/categorias`, `prod/solicitadoEm`. Com duplicidade, nada vai ao
  sistema: o processo fica com `lancarStatus: "duplicidade"` e `prod/status: "lancar"` até
  o juiz usar "Lançar mesmo assim" (grava com `duplicidadeConfirmada: true`).
- **Aprovar para revisão** cria `minutas/painel-ia-<id>` (item 1 acima: `claude_ia`,
  pendente) pela mesma transação condicional, com `origem: "painel-gabinete"` e a trava em
  `efeitosGabinete/painel-ia-<id>`, e grava `prod/status: "enviada"`, `prod/enviadaEm`,
  `prod/minutaId`. Também confere a duplicidade ("Registrar mesmo assim").
- **Conciliação**: a sessão do juiz confere as minutas vivas pelo `painelId`. Minuta
  assinada no sistema (por qualquer caminho) vira `prod/status: "lancada"` (ou
  `"assinada"`, se o registro é do Claude IA) com `prod/lancadaEm` e `prod/minutaId`;
  minuta do Claude IA pendente ou com correção pedida espelha `prod/status`
  `"pendente"`/`"correcao"`.
- Consequência para o executor: enviar `prod.status` `"aprovada"`/`"lancar"` (Passo 2B) e
  confirmar lançados (Passo 2C) deixam de ser necessários para a esteira. Se o executor
  encontrar um processo com `"lancar"` e `lancarStatus: "duplicidade"`, não deve lançar: a
  decisão é do juiz, na aba.

### `gabinete/sistema/*`

Mesmos campos de `sistema/*` no artifact:

| Nó | Quem grava | Conteúdo |
|---|---|---|
| `gabinete/sistema/gatilho` | aba e executor | aba: `{status: "pendente", modo: "completo", pedidoEm, pedidoPor}`, por transação (não grava se já houver `pendente` ou `disparado`); executor: `status: "disparado"` com `disparadoEm` e, ao terminar, `status: "atendido"` com `atendidoEm` |
| `gabinete/sistema/executor` | executor | `{captchaEm, ultimaVerificacao}` (sinal de vida; `captchaEm` vazio quando não há captcha) |
| `gabinete/sistema/trava` | executor | `{status: "livre" \| …, liberadaEm}`; a aba mostra a trava quando não está livre |
| `gabinete/sistema/varredura` | executor | `{importados, pasta, ultimaVarreduraLocal}` (hora local, sem fuso) |

Regra do juiz: **o executor só roda quando ele aperta "Ativar o executor"**. A tarefa
agendada confere o `gatilho` a cada 5 minutos, das 6h às 23h, e consome o pedido; nada
rearma o gatilho sozinho. A aba só pede o modo `completo`: os modos `sincronizar` e
`confirmar` do Painel ficaram sem uso, porque lançamento, aprovação e conferência agora
acontecem dentro do sistema.

### O que deixou de existir

- `sistema/produtividade` (snapshot copiado para o Painel) e a ponte manual de
  copiar/colar: a aba usa os dados vivos. O `snapshotPainel/` continua sendo publicado
  pela sessão do juiz enquanto o executor o ler.
- A Visão geral e a Produtividade do Painel: o sistema já tem esses painéis.
