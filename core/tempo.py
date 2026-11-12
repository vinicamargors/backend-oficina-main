from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FUSO_BR = ZoneInfo("America/Sao_Paulo")


def agora_br() -> datetime:
    """Agora no horário de Brasília, independente do fuso do servidor (a VM roda em UTC)."""
    return datetime.now(FUSO_BR)


def para_br(valor: str) -> datetime:
    """Timestamp do banco (UTC, 'Z' ou '+00:00') como relógio de parede de Brasília, sem fuso.

    Sem isso uma OS fechada às 22h BRT cai no dia seguinte e some do período filtrado.
    """
    dt = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(FUSO_BR).replace(tzinfo=None)
