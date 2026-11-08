# Proposta de regras do banco por papel

Situação em 08/11/2026: `database.rules.json` libera leitura e escrita de **todo** o banco
para quatro UIDs autenticados (juiz, Gilbert, Laíse e a conta do gabinete). Isso já fecha o
banco para quem não tem conta. Mas qualquer um dos quatro ainda pode alterar ou apagar
qualquer nó, inclusive as minutas dos colegas, as metas do magistrado e o Acervo.

Este arquivo é **só uma proposta**. O `database.rules.json` não foi alterado. Antes de publicar:

1. preencha os UIDs (Firebase console → Authentication → Users → coluna "User UID");
2. teste no **Simulador de regras** do console (Realtime Database → Regras → Simulador), com
   cada UID, nos casos da seção "Como testar";
3. publique em horário sem uso e abra o sistema com cada conta.

## Papéis

| Papel | Conta | UID | `assessorId` nas minutas |
|---|---|---|---|
| Juiz | juiz | `<UID do juiz>` | `juiz` |
| Conta do gabinete (executor, scripts) | gabinete-auto | `<UID da conta do gabinete>` | `claude_ia` / `juiz` (conforme o contrato) |
| Assessor | gilbert | `<UID do Gilbert>` | `assessor1` |
| Assessor | laise | `<UID da Laíse>` | `assessor2` |

Regra geral pedida: **juiz e conta do gabinete gravam tudo; assessores gravam só as próprias
minutas e o Balcão; `acervo/*` só juiz e gabinete** (com uma exceção: a confirmação de versão de
cada assessor, ver abaixo). Todos os quatro leem tudo.

## O que o sistema grava hoje, por papel (levantado no código)

Antes de restringir, é preciso saber o que cada tela grava quando quem está logado é um
assessor. Se a regra negar uma dessas gravações, a tela passa a mostrar o erro de permissão
(desde 08/11/2026 o sistema mostra o motivo real da falha).

| Nó | Quem grava hoje | Observação |
|---|---|---|
| `minutas/<id>` | todos | assessor registra, edita, exclui (exclusão lógica) e marca correção nas **próprias**; juiz assina, pede correção e edita qualquer uma; o gabinete grava `painel-ia-*` e `painel-*` |
| `pedidosBalcao/<id>` | todos | assessor cadastra, edita, marca como minutado, cancela e exclui; a sincronização da minuta dá baixa no pedido do mesmo processo |
| `notificacoesJuiz/<id>` | todos | o assessor cria a notificação de "despacho virtual" pelo Balcão; a sincronização marca `lida`; o juiz marca e exclui |
| `processosMeta*/<id>` | todos | cadastro e importação pelas Metas; a sincronização da minuta do **assessor** atualiza `ultimaMovimentacao`, `ultimaMinutaId`, `ultimaMinutaTipo`, `editadoPor`, `editadoEm` e a fase |
| `obsAcompanhamento/<chave>` | todos | observações do painel 180/120/100 |
| `assessores` | todos | gravado uma única vez se o nó não existir (dados iniciais) |
| `metasJuizDiario/<data>` | juiz | contadores do magistrado |
| `efeitosGabinete/<id>` | juiz | trava dos efeitos das minutas do gabinete (só a sessão do juiz processa) |
| `snapshotPainel` | juiz | snapshot lido pelo executor |
| `acervo/*` | juiz (publicação) e assessor (só `acervo/confirmacoes/<usuario>`) | a confirmação "meu Claude está na versão X" é gravada pelo próprio assessor |

Pontos que pedem decisão do juiz (marcados **[DECIDIR]** nas regras abaixo):

- **Sincronização feita pela sessão do assessor**: ao registrar minuta, o sistema atualiza o
  processo nas Metas (`processosMeta*`) e marca a notificação como lida. A proposta permite ao
  assessor gravar **só esses campos** nas Metas; a alternativa é negar e deixar a sincronização
  só para a sessão do juiz (exigiria mudar o código, para não mostrar erro ao assessor).
- **Metas CNJ (cadastro e importação de processos)**: hoje qualquer um cadastra. A proposta
  deixa cadastro, edição e exclusão só para juiz e gabinete.
- **Observações do 180/120/100**: a proposta permite ao assessor (é anotação de trabalho).
- **Balcão**: pedido pede que assessores gravem o Balcão; a proposta não restringe por autor
  (o Balcão é compartilhado: um assessor dá baixa no pedido cadastrado pelo outro). Exclusão
  física de pedido poderia ficar só para o juiz (opcional, comentado).
- **Status `assinada`**: a proposta impede o assessor de marcar a própria minuta como
  assinada ou de alterar minuta já assinada (só o juiz assina).

## Regras propostas

Formato do Realtime Database. Os UIDs entre `< >` são para o juiz preencher (troque o texto
inteiro, inclusive os sinais, pelo UID entre aspas simples, como já está no arquivo atual).

```json
{
  "rules": {
    ".read": "auth != null && (auth.uid === '<UID do juiz>' || auth.uid === '<UID da conta do gabinete>' || auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>')",
    ".write": "auth != null && (auth.uid === '<UID do juiz>' || auth.uid === '<UID da conta do gabinete>')",

    "minutas": {
      "$id": {
        ".write": "auth != null && (auth.uid === '<UID do juiz>' || auth.uid === '<UID da conta do gabinete>' || ((auth.uid === '<UID do Gilbert>' && (!data.exists() || data.child('assessorId').val() === 'assessor1') && (!newData.exists() || newData.child('assessorId').val() === 'assessor1')) || (auth.uid === '<UID da Laíse>' && (!data.exists() || data.child('assessorId').val() === 'assessor2') && (!newData.exists() || newData.child('assessorId').val() === 'assessor2'))) && data.child('status').val() !== 'assinada' && newData.child('status').val() !== 'assinada')",
        "efeitosAplicados": {
          ".validate": "auth.uid === '<UID do juiz>' || auth.uid === '<UID da conta do gabinete>' || newData.val() === data.val()"
        }
      }
    },

    "pedidosBalcao": {
      ".write": "auth != null && (auth.uid === '<UID do juiz>' || auth.uid === '<UID da conta do gabinete>' || auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>')"
    },

    "notificacoesJuiz": {
      "$id": {
        ".write": "auth != null && (auth.uid === '<UID do juiz>' || auth.uid === '<UID da conta do gabinete>' || ((auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>') && newData.exists() && (!data.exists() || newData.child('lida').val() === true)))"
      }
    },

    "obsAcompanhamento": {
      ".write": "auth != null && (auth.uid === '<UID do juiz>' || auth.uid === '<UID da conta do gabinete>' || auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>')"
    },

    "processosMetaImprobidade":    { "$id": { "$campo": { ".write": "auth != null && (auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>') && data.parent().exists() && ($campo === 'ultimaMovimentacao' || $campo === 'ultimaMinutaId' || $campo === 'ultimaMinutaTipo' || $campo === 'fase' || $campo === 'editadoEm' || $campo === 'editadoPor')" } } },
    "processosMetaAcoesColetivas": { "$id": { "$campo": { ".write": "auth != null && (auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>') && data.parent().exists() && ($campo === 'ultimaMovimentacao' || $campo === 'ultimaMinutaId' || $campo === 'ultimaMinutaTipo' || $campo === 'fase' || $campo === 'editadoEm' || $campo === 'editadoPor')" } } },
    "processosMetaMaisDezAnos":    { "$id": { "$campo": { ".write": "auth != null && (auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>') && data.parent().exists() && ($campo === 'ultimaMovimentacao' || $campo === 'ultimaMinutaId' || $campo === 'ultimaMinutaTipo' || $campo === 'fase' || $campo === 'editadoEm' || $campo === 'editadoPor')" } } },
    "processosMetaSaude":          { "$id": { "$campo": { ".write": "auth != null && (auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>') && data.parent().exists() && ($campo === 'ultimaMovimentacao' || $campo === 'ultimaMinutaId' || $campo === 'ultimaMinutaTipo' || $campo === 'fase' || $campo === 'editadoEm' || $campo === 'editadoPor')" } } },

    "acervo": {
      "confirmacoes": {
        "gilbert": { ".write": "auth != null && auth.uid === '<UID do Gilbert>'" },
        "laise":   { ".write": "auth != null && auth.uid === '<UID da Laíse>'" }
      }
    },

    "assessores": {
      ".write": "auth != null && !data.exists() && (auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>')"
    }
  }
}
```

### Como as regras se combinam

- No Realtime Database, **uma permissão concedida num nó vale para tudo abaixo dele e não pode ser
  retirada mais abaixo**. Por isso a raiz concede escrita só ao juiz e ao gabinete, e cada nó
  acrescenta o que os assessores podem gravar. Nós não listados (`metasJuizDiario`,
  `efeitosGabinete`, `snapshotPainel`, o restante de `acervo`) ficam só para juiz e gabinete.
- `minutas/$id`: o assessor só cria, altera ou exclui (logicamente) a minuta cujo `assessorId` é
  o dele, antes e depois da gravação; não consegue mudar o autor, assinar, nem mexer numa minuta
  assinada. As gravações parciais (`update` de campos) avaliam `newData` como o registro inteiro
  resultante, então a regra continua valendo. **[DECIDIR]** se o assessor deve poder alterar
  minuta já assinada (hoje pode; a proposta proíbe).
- `notificacoesJuiz/$id`: o assessor cria notificação nova e marca como lida; não apaga.
- `processosMeta*`: o assessor só atualiza os campos que a sincronização grava, em processo que
  já existe. **[DECIDIR]** — conferir no código, antes de publicar, a lista exata de campos de
  `sincronizarAbasPorMinuta` (em 08/11/2026: `ultimaMovimentacao`, `ultimaMinutaId`, `ultimaMinutaTipo`,
  `editadoPor`, `editadoEm` e `fase` quando a sentença muda a fase); se gravar outro campo, acrescentá-lo à lista ou a gravação falha.
- `acervo/confirmacoes/<usuario>`: cada assessor grava só a própria confirmação.
- `assessores`: o assessor só pode criar o nó se ele ainda não existir (dados iniciais).
- Opcional, Balcão: para reservar a **exclusão física** de pedidos ao juiz, troque a regra de
  `pedidosBalcao` por uma em `$id` com `... || ((auth.uid === '<UID do Gilbert>' || auth.uid === '<UID da Laíse>') && newData.exists())`.

### Como testar (Simulador de regras)

| # | Conta | Operação | Esperado |
|---|---|---|---|
| 1 | Gilbert | `set` em `minutas/teste1` com `assessorId: "assessor1"`, `status: "pendente"` | permitido |
| 2 | Gilbert | `set` em `minutas/teste2` com `assessorId: "assessor2"` | negado |
| 3 | Gilbert | `update` em minuta da Laíse | negado |
| 4 | Gilbert | `update` `status: "assinada"` na própria minuta | negado |
| 5 | Juiz | `update` `status: "assinada"` em minuta de assessor | permitido |
| 6 | Laíse | `push` em `pedidosBalcao` | permitido |
| 7 | Laíse | `set` em `acervo/meta/versao` | negado |
| 8 | Laíse | `set` em `acervo/confirmacoes/laise` | permitido |
| 9 | Laíse | `set` em `acervo/confirmacoes/gilbert` | negado |
| 10 | Gilbert | `set` em `metasJuizDiario/2026-11-08/distribuicao` | negado |
| 11 | Gilbert | `set` em `processosMetaSaude/<id existente>/ultimaMovimentacao` | permitido |
| 12 | Gilbert | `remove` em `processosMetaSaude/<id>` | negado |
| 13 | Conta do gabinete | `set` em `minutas/painel-ia-teste` e em `efeitosGabinete/x` | permitido |
| 14 | Sem login | leitura de `/minutas` | negado |

Depois de publicar, abra o sistema com cada conta e faça o fluxo real: o assessor registra uma
minuta de um processo que está nas Metas e no Balcão (deve dar certo, com a mensagem "Abas
atualizadas"); o juiz assina; o assessor tenta excluir uma minuta da colega (deve aparecer
"permissão negada").
