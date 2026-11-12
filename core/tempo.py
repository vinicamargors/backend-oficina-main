from datetime import datetime
from zoneinfo import ZoneInfo

FUSO_BR = ZoneInfo("America/Sao_Paulo")


def agora_br() -> datetime:
    """Agora no horário de Brasília, independente do fuso do servidor (a VM roda em UTC)."""
    return datetime.now(FUSO_BR)
