import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis do .env para não expor chave no GitHub
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
service_key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# Mão invisível conectando seu backend ao banco
supabase: Client = create_client(url, key)

# O Dono do Cofre (pode criar usuários no Auth ignorando regras de Row Level Security)
supabase_admin: Client = create_client(url, service_key)