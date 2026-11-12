"""Token do link público de avaliação: `<os_id>.<assinatura>`, assinado com HMAC-SHA256. Só stdlib."""
import base64
import hashlib
import hmac
import os
from typing import Optional
from uuid import UUID


def _chave() -> bytes:
    # shortcut: sem AVALIACAO_SECRET, deriva da SUPABASE_SERVICE_KEY (sempre presente); trocar essa chave invalida links já enviados.
    # Defina AVALIACAO_SECRET para os links sobreviverem à rotação da service key.
    base = os.getenv("AVALIACAO_SECRET") or os.getenv("SUPABASE_SERVICE_KEY") or ""
    if not base:
        raise RuntimeError("AVALIACAO_SECRET ou SUPABASE_SERVICE_KEY precisa estar definida.")
    return hashlib.sha256(b"avaliacao-os:" + base.encode()).digest()


def _assinar(os_id: str) -> str:
    mac = hmac.new(_chave(), os_id.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).rstrip(b"=").decode()


def gerar_token(os_id: str) -> str:
    return f"{os_id}.{_assinar(os_id)}"


def ler_token(token: str) -> Optional[str]:
    """Devolve o os_id se a assinatura confere; senão None (sem distinguir o motivo)."""
    os_id, _, assinatura = (token or "").partition(".")
    try:
        UUID(os_id)
    except ValueError:
        return None
    if not hmac.compare_digest(assinatura.encode(), _assinar(os_id).encode()):
        return None
    return os_id
