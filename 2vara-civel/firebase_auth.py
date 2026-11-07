"""Acesso autenticado ao banco do sistema de produtividade (conta gabinete-auto).

Lê as credenciais de firebase-credencial.json (mesma pasta deste arquivo ou o
caminho indicado), faz login, renova o token sozinho e expõe get/put/patch.
Nunca imprime a senha nem o token. Só usa a biblioteca padrão do Python.

Uso:
    from firebase_auth import Banco
    banco = Banco()
    snapshot = banco.get("snapshotPainel")
    banco.put("minutas/painel-ia-ABC123", minuta)
    banco.patch("minutas/painel-ia-ABC123", {"status": "assinada"})
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DB = "https://produtividade-2vara-civel-default-rtdb.firebaseio.com"
MARGEM_RENOVACAO = 300  # renova 5 minutos antes de vencer


class ErroBanco(Exception):
    pass


def _post(url, corpo, tipo="application/json"):
    dados = json.dumps(corpo).encode() if tipo == "application/json" else urllib.parse.urlencode(corpo).encode()
    req = urllib.request.Request(url, data=dados, headers={"Content-Type": tipo})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e)["error"]["message"]
        except Exception:
            msg = f"HTTP {e.code}"
        raise ErroBanco(f"Falha na autenticação: {msg}") from None


class Banco:
    def __init__(self, arquivo_credencial=None):
        caminho = Path(arquivo_credencial or Path(__file__).with_name("firebase-credencial.json"))
        cred = json.loads(caminho.read_text(encoding="utf-8"))
        self._api_key = cred["apiKey"]
        self._email = cred["email"]
        self._senha = cred["password"]
        self._token = None
        self._refresh = None
        self._vence_em = 0.0

    # ---------- autenticação ----------
    def _login(self):
        r = _post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self._api_key}",
            {"email": self._email, "password": self._senha, "returnSecureToken": True},
        )
        self._guardar(r["idToken"], r["refreshToken"], r["expiresIn"])

    def _renovar(self):
        r = _post(
            f"https://securetoken.googleapis.com/v1/token?key={self._api_key}",
            {"grant_type": "refresh_token", "refresh_token": self._refresh},
            tipo="application/x-www-form-urlencoded",
        )
        self._guardar(r["id_token"], r["refresh_token"], r["expires_in"])

    def _guardar(self, token, refresh, expira_seg):
        self._token, self._refresh = token, refresh
        self._vence_em = time.time() + int(expira_seg)

    def token(self, forcar=False):
        if forcar or not self._token or time.time() > self._vence_em - MARGEM_RENOVACAO:
            if self._refresh and not forcar:
                try:
                    self._renovar()
                except ErroBanco:
                    self._login()
            else:
                self._login()
        return self._token

    # ---------- banco ----------
    def _chamar(self, metodo, caminho, corpo=None, tentar_de_novo=True):
        url = f"{BASE_DB}/{caminho.strip('/')}.json?auth={urllib.parse.quote(self.token())}"
        dados = None if corpo is None else json.dumps(corpo).encode()
        req = urllib.request.Request(url, data=dados, method=metodo, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 401 and tentar_de_novo:
                self.token(forcar=True)
                return self._chamar(metodo, caminho, corpo, tentar_de_novo=False)
            raise ErroBanco(f"{metodo} /{caminho}: HTTP {e.code}") from None

    def get(self, caminho):
        return self._chamar("GET", caminho)

    def put(self, caminho, dados):
        return self._chamar("PUT", caminho, dados)

    def patch(self, caminho, dados):
        return self._chamar("PATCH", caminho, dados)


if __name__ == "__main__":
    # Teste rápido: lê o snapshot sem gravar nada
    b = Banco()
    snap = b.get("snapshotPainel")
    print("OK — leitura autenticada funcionou." if snap is not None else "OK — autenticado (snapshotPainel vazio).")
