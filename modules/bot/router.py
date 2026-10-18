from fastapi import APIRouter, Depends
from core.security import validar_chave_bot
from . import schemas, service

router = APIRouter(dependencies=[Depends(validar_chave_bot)])


# ---------------------------------------------------------
# 1. AUTENTICAÇÃO E IDENTIFICAÇÃO (Para o Typebot saber quem fala)
# ---------------------------------------------------------
@router.post("/identificar")
def identificar_mecanico(req: schemas.IdentificarRequest):
    """
    O Typebot envia o telemóvel do WhatsApp.
    Devolvemos o ID da Empresa, ID do Mecânico e o Nome.
    Se não existir, devolvemos erro e o Typebot bloqueia a entrada.
    """
    return service.identificar_mecanico(req.telefone)

# ---------------------------------------------------------
# 2. CONSULTAS E BUSCAS
# ---------------------------------------------------------
@router.post("/buscar-veiculo")
def buscar_veiculo(req: schemas.BuscaRequest):
    """
    O Typebot pede: "Marcio da Parati".
    Devolvemos a lista ranqueada de clientes/veículos.
    """
    return service.buscar_cliente_veiculo_cruzado(req.empresa_id, req.termo)

@router.post("/historico-veiculo")
def historico_veiculo(req: dict):
    """Devolve a lista de OSs anteriores de um veículo (paginável no Typebot)"""
    # Exige: {"empresa_id": "...", "veiculo_id": "..."}
    return service.buscar_historico_os_por_veiculo(req.get("empresa_id"), req.get("veiculo_id"))

@router.post("/buscar-os-ativa")
def buscar_os_ativa(req: schemas.BuscaRequest):
    """Traz as OSs em andamento pela placa ou nome do cliente"""
    return service.buscar_os_ativa_por_placa_cliente(req.empresa_id, req.termo)

# ---------------------------------------------------------
# 3. MÁQUINA DE ABERTURA DE ORDEM DE SERVIÇO
# ---------------------------------------------------------
@router.post("/abrir-os")
def abrir_os_existente(req: schemas.CriarOSRequest):
    """Abre uma OS para um carro que já está na base"""
    return service.abrir_os(req)

@router.post("/cadastro-rapido")
async def cadastro_rapido(req: schemas.CadastroRapidoRequest):
    """
    O fluxo brutal: Recebe Nome, Telefone e Placa do Typebot.
    Bate na API do Detran, cria Cliente, cria Veículo, cria OS e devolve o ID.
    """
    return await service.executar_cadastro_rapido(req)

@router.post("/atualizar-os-dados")
def atualizar_os_dados(req: schemas.AtualizarOSRequest):
    """Injeta a KM e o relato do problema na OS recém-aberta"""
    return service.atualizar_dados_os(req)

# ---------------------------------------------------------
# 4. INTELIGÊNCIA ARTIFICIAL E ÁUDIO
# ---------------------------------------------------------
@router.post("/ia/processar-audio")
async def processar_audio_typebot(req: schemas.ProcessarAudioRequest):
    """
    O Typebot envia o URL do áudio gravado no WhatsApp.
    O FastAPI faz o download, transcreve com o Whisper, 
    estrutura com o Gemini e INJETA os itens na OS automaticamente.
    """
    return await service.processar_e_injetar_audio(req)