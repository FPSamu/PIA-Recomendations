from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables del archivo .env

def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Supabase URL or KEY not found in environment variables")

    return create_client(url, key)
