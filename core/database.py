import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis do .env para não expor chave no GitHub
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
service_key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# Backend usa só a service_role: o RLS fica fechado para anon e o isolamento por empresa
# é garantido em core/security.py (validar_passaporte).
supabase: Client = create_client(url, service_key)
supabase_admin: Client = supabase
