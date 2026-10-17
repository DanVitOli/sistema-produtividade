# Integração automática Gabinete → Sistema

O executor do gabinete grava as minutas **direto no banco do sistema** pela
REST do Firebase. A sessão do juiz aberta no sistema completa sozinha os
efeitos (categorias dos painéis Meta 2 e 180/120/100, sincronização das abas,
baixa no Balcão e contadores das metas do magistrado) e publica o snapshot do
Painel em `snapshotPainel/`. **Nenhum copiar/colar é necessário.**

Base: `https://produtividade-2vara-civel-default-rtdb.firebaseio.com`

## 1. Registrar minuta da IA (pendente de revisão/assinatura)

`PUT /minutas/painel-ia-<painelId>.json` — a chave determinística torna o
envio idempotente (reenviar não duplica).

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

`PUT /minutas/painel-<painelId>.json` — mesma chave usada pelo botão manual
"Lançar assinadas", então os dois caminhos nunca duplicam.

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
- **Efeitos**: o campo `efeitosAplicados` é preenchido pelo sistema; nunca o
  envie. Os contadores das metas do magistrado só são incrementados para
  minutas com `assessorId: "juiz"`.
- Exemplo com curl:

```bash
curl -sS -X PUT \
  "https://produtividade-2vara-civel-default-rtdb.firebaseio.com/minutas/painel-ia-ABC123.json" \
  -H 'Content-Type: application/json' \
  -d @minuta.json
```
