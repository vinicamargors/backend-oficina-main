"""Formas de pagamento aceitas, definidas UMA vez. O front lê a lista em GET /api/v1/formas-pagamento."""
from typing import Annotated, Optional

from pydantic import AfterValidator

FORMAS_PAGAMENTO = ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Boleto / Faturado", "TED / Transferência"]


def _valida(v: Optional[str]) -> Optional[str]:
    if v is not None and v not in FORMAS_PAGAMENTO:
        raise ValueError("Forma de pagamento inválida. Use: " + ", ".join(FORMAS_PAGAMENTO) + ".")
    return v


# Só em corpos de ENTRADA: linhas antigas do banco com outra forma continuam sendo lidas sem erro.
FormaPagamento = Annotated[Optional[str], AfterValidator(_valida)]
