import os
from dotenv import load_dotenv
from supabase.client import Client, create_client

load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def verify_data():
    kb_count = supabase.table("knowledge_base").select("id", count="exact").execute()
    status_count = supabase.table("author_status").select("email", count="exact").execute()
    log_count = supabase.table("bot_logs").select("id", count="exact").execute()
    
    print(f"--- Database Status ---")
    print(f"Knowledge Base Chunks: {kb_count.count}")
    print(f"Author Records: {status_count.count}")
    print(f"Interaction Logs: {log_count.count}")

if __name__ == "__main__":
    verify_data()
