import os
from dotenv import load_dotenv
import httpx
from supabase import create_client, Client, ClientOptions

# Carrega as variáveis do .env para não expor chave no GitHub
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
service_key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# O cliente padrão do supabase-py usa HTTP/2 numa única conexão compartilhada entre as threads do FastAPI;
# com requisições simultâneas ela quebra (httpx.ReadError / ConnectionTerminated). HTTP/1.1 com pool é seguro.
_http = httpx.Client(
    http2=False,
    timeout=httpx.Timeout(30.0, connect=10.0),
    limits=httpx.Limits(max_connections=40, max_keepalive_connections=20),
)

# Backend usa só a service_role: o RLS fica fechado para anon e o isolamento por empresa
# é garantido em core/security.py (validar_passaporte).
supabase: Client = create_client(url, service_key, options=ClientOptions(httpx_client=_http))
supabase_admin: Client = supabase
